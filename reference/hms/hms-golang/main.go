package main

import (
	"bufio"
	"context"
	"encoding/json"
	"flag"
	"fmt"
	"io"
	"os"
	"os/exec"
	"path/filepath"
	"strings"
	"sync"
	"time"

	"github.com/rs/zerolog"
)

/* ---------- logging ------------------------------------------------------ */

var log zerolog.Logger
func configureLogger(format string) {
	var writer io.Writer
	if format == "text" {
		// Colorized text
		writer = zerolog.ConsoleWriter{
			Out:        os.Stdout,
			TimeFormat: time.RFC3339,
		}
	} else {
		// JSON
		writer = os.Stdout
	}
	log = zerolog.
		New(writer).
		With().
		Timestamp().
		Logger().
		Level(zerolog.InfoLevel)
} 

const hmsRunner = "hms-runner"

func logInfo(src, m string)   { log.Info().Str("source", src).Msg(m) }
func logWarn(src, m string)   { log.Warn().Str("source", src).Msg(m) }
func logError(src, m string)  { log.Error().Str("source", src).Msg(m) }

/* ---------- CLI flags ---------------------------------------------------- */

type cliCfg struct {
	projectFile string
	simName     string
	example     bool
	jsonFile    string
	logFormat   string
}

func parseFlags() cliCfg {
	var c cliCfg
	flag.StringVar(&c.projectFile, "project-file", "",     ".hms project file")
	flag.StringVar(&c.simName,     "sim-name",     "",     "simulation name")
	flag.BoolVar(&c.example,       "example",      false,  "built-in example (tenk)")
	flag.StringVar(&c.jsonFile,    "json-file",    "",     "JSON file with hms_schema")
	flag.StringVar(&c.logFormat,   "log-format",   "text", "text | json")
	flag.Parse()
	return c
}

/* ---------- helpers ------------------------------------------------------ */

const jythonTpl = `from hms.model.JythonHms import *
OpenProject("%s", "%s")
ComputeRun("%s")
SaveAllProjectComponents()
`

func buildJython(projectName, projectDir, simName string) (string, error) {
	tmp, err := os.CreateTemp("", "*.script")
	if err != nil {
		return "", err
	}
	code := fmt.Sprintf(jythonTpl, projectName, projectDir, simName)
	if _, err = tmp.WriteString(code); err != nil {
		return "", err
	}
	tmp.Close()
	return tmp.Name(), nil
}

func classifyAndLog(source, line string) {
	switch {
	case strings.Contains(line, "WARNING"):
		logWarn(source, line)
	case strings.Contains(line, "ERROR"):
		logError(source, line)
	case strings.Contains(line, "NOTE"):
		logInfo(source, line)
	default:
		logInfo(source, line)
	}
}

/* ---------- tailing files with WaitGroup ------------------------------- */

func tailFile(ctx context.Context, path string, wg *sync.WaitGroup) {
	defer wg.Done()

	cmd := exec.CommandContext(ctx, "tail", "-n", "0", "-F", path)
	stdout, _ := cmd.StdoutPipe()
	if err := cmd.Start(); err != nil {
		logError(path, "tail failed: "+err.Error())
		return
	}

	sc := bufio.NewScanner(stdout)
	for sc.Scan() {
		classifyAndLog(path, strings.TrimSpace(sc.Text()))
	}

	_ = cmd.Wait()
}

/* ---------- main workflow ------------------------------------------------ */

func main() {
	cfg := parseFlags()
	configureLogger(cfg.logFormat)

	// --- input validation -------------------------------------------------
	gotInput := 0
	if cfg.example {
		gotInput++
	}
	if cfg.jsonFile != "" {
		gotInput++
	}
	if cfg.projectFile != "" || cfg.simName != "" {
		gotInput++
	}
	if gotInput != 1 {
		logError(hmsRunner, "Specify exactly one of --example, --json-file, or --project-file/--sim-name")
		os.Exit(1)
	}

	var (
		hmsFile string
		simName string
	)

	hmsHome := os.Getenv("HMS_HOME")
	switch {
	case cfg.example:
		hmsFile = filepath.Join(hmsHome, "samples", "tenk", "tenk.hms")
		simName = "Jan 96 storm"

	case cfg.jsonFile != "":
		f, e := os.Open(cfg.jsonFile)
		if e != nil {
			logError(hmsRunner, "cannot read JSON file: "+e.Error())
			os.Exit(1)
		}
		var data struct {
			Schema struct {
				ProjectFile string `json:"project_file"`
				SimName     string `json:"sim_name"`
			} `json:"hms_schema"`
		}
		if e = json.NewDecoder(f).Decode(&data); e != nil {
			logError(hmsRunner, "invalid JSON: "+e.Error())
			os.Exit(1)
		}
		hmsFile, simName = data.Schema.ProjectFile, data.Schema.SimName

	default:
		hmsFile, simName = cfg.projectFile, cfg.simName
	}

	if hmsFile == "" || !strings.HasSuffix(strings.ToLower(hmsFile), ".hms") {
		logError(hmsRunner, "project_file must be a .hms file")
		os.Exit(1)
	}
	if simName == "" {
		logError(hmsRunner, "sim_name is required")
		os.Exit(1)
	}

	projectDir := filepath.Dir(hmsFile)
	projectName := strings.TrimSuffix(filepath.Base(hmsFile), filepath.Ext(hmsFile))

	// --- build Jython script ---------------------------------------------
	scriptPath, e := buildJython(projectName, projectDir, simName)
	if e != nil {
		logError(hmsRunner, "cannot write temp script: "+e.Error())
		os.Exit(1)
	}
	defer os.Remove(scriptPath)

	// --- discover & start tailers with WaitGroup ------------------------
	ctx, cancel := context.WithCancel(context.Background())
	defer cancel()

	var wg sync.WaitGroup

	for _, pattern := range []string{"*.log", "*.out"} {
		files, _ := filepath.Glob(filepath.Join(projectDir, pattern))
		for _, p := range files {
			wg.Add(1)
			go tailFile(ctx, p, &wg)
		}
	}

	// --- build Java command ----------------------------------------------
	javaExe := filepath.Join(hmsHome, "jre", "bin", "java")
	classpath := fmt.Sprintf("%s/*:%s/lib/*", hmsHome, hmsHome)

	javaArgs := []string{
		"-DMapPanel.NoVolatileImage=true",
		"-Xms32M",
		"-Dpython.path=",
		"-Dpython.home=.",
		"-Djava.library.path=" + filepath.Join(hmsHome, "bin")+":"+filepath.Join(hmsHome, "bin", "gdal"),
		"-classpath", classpath,
		"hms.Hms",
		"-s", scriptPath,
	}

	cmd := exec.Command(javaExe, javaArgs...)
	cmdEnv := os.Environ()
	cmdEnv = append(cmdEnv,
		"PATH="+filepath.Join(hmsHome, "bin", "taudem")+":"+filepath.Join(hmsHome, "bin", "mpi")+":"+os.Getenv("PATH"),
		"GDAL_DATA="+filepath.Join(hmsHome, "bin", "gdal", "gdal-data"),
		"PROJ_LIB="+filepath.Join(hmsHome, "bin", "gdal", "proj"),
	)
	cmd.Env = cmdEnv

	stdout, _ := cmd.StdoutPipe()
	cmd.Stderr = cmd.Stdout // merge

	if e = cmd.Start(); e != nil {
		logError(hmsRunner, "cannot start HMS: "+e.Error())
		os.Exit(1)
	}

	// --- stream HMS stdout/stderr ---------------------------------------
	go func(r io.Reader) {
		sc := bufio.NewScanner(r)
		for sc.Scan() {
			line := strings.TrimSpace(sc.Text())
			if line != "" {
				classifyAndLog("hms-stdout-stderr", line)
			}
		}
	}(stdout)

	if e = cmd.Wait(); e != nil {
		if exitErr, ok := e.(*exec.ExitError); ok {
			logError(hmsRunner, fmt.Sprintf("HMS exited with code %d", exitErr.ExitCode()))
			os.Exit(exitErr.ExitCode())
		}
		logError(hmsRunner, e.Error())
		os.Exit(1)
	}

	// --- give tailers a moment to catch remaining writes -----------------
	time.Sleep(1 * time.Second)
	cancel() // signal tailers to stop
	wg.Wait() // wait for tailers to finish

	logInfo(hmsRunner, fmt.Sprintf("Simulation '%s' completed for project '%s'.", simName, projectName))
}

