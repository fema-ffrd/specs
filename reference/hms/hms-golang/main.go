package main

import (
	"bufio"
	"context"
	"encoding/json"
	// "flag"
	"fmt"
	"io"
	"os"
	"os/exec"
	"path/filepath"
	"regexp"
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
	projectFile  string
	simName      string
	excessPrecip string
	jsonFile     string
	example      bool
	logFormat    string
}

<<<<<<< HEAD
// func parseFlags() cliCfg {
// 	var c cliCfg
// 	flag.StringVar(&c.projectFile, "project-file", "",     ".hms project file")
// 	flag.StringVar(&c.simName,     "sim-name",     "",     "simulation name")
// 	flag.BoolVar(&c.example,       "example",      false,  "built-in example (tenk)")
// 	flag.StringVar(&c.jsonFile,    "json-file",    "",     "JSON file with hms_schema")
// 	flag.StringVar(&c.logFormat,   "log-format",   "text", "text | json")
// 	flag.Parse()
// 	return c
// }
/* ---------- json args ----------------------------------------------------- */
// // Struct for CLI and JSON args
// type cliCfg struct {
// 	projectFile string
// 	simName     string
// 	example     bool
// 	logFormat   string
// }

// Define structs to map the JSON fields
// This will help in mapping all fields from the JSON payload to variables
type Payload struct {
	Name       string                 `json:"name"`
	Type       string                 `json:"type"`
	Attributes map[string]interface{} `json:"attributes"`
	Inputs     []Input                `json:"inputs"`
	Outputs    []Output               `json:"outputs"`
	Stores     []Store                `json:"stores"`
}

type Input struct {
	Name      string                 `json:"name"`
	Paths     map[string]interface{} `json:"paths"`
	StoreName string                 `json:"store_name"`
	StoreRoot string                 `json:"store_root"`
	StoreType string                 `json:"store_type"`
}

type Output struct {
	Name      string                 `json:"name"`
	Paths     map[string]interface{} `json:"paths"`
	StoreName string                 `json:"store_name"`
	StoreRoot string                 `json:"store_root"`
	StoreType string                 `json:"store_type"`
}

type Store struct {
	Name   string                 `json:"name"`
	Params map[string]interface{} `json:"params"`
	Type   string                 `json:"store_type"`
}

// // Update the extractCliCfgFromPayload function to map all fields
// func extractPayload(jsonPath string) (Payload, error) {
// 	var payload Payload
// 	file, err := os.Open(jsonPath)
// 	if err != nil {
// 		return payload, err
// 	}
// 	defer file.Close()

// 	if err = json.NewDecoder(file).Decode(&payload); err != nil {
// 		return payload, err
// 	}
// 	return payload, nil
// }

func populateCliCfgFromPayload(payload Payload) cliCfg {
    var c cliCfg

    // Assign projectFile from the first input with name "hms" and path "hms-project-file"
    for _, inp := range payload.Inputs {
        if inp.Name == "hms" {
            if pf, ok := inp.Paths["hms-project-file"].(string); ok {
                c.projectFile = pf
            }
            break
        }
    }

	for _, out := range payload.Outputs {
		if out.Name == "excess-precip" {
			if ep, ok := out.Paths["excess-precip"].(string); ok {
				c.excessPrecip = ep
			}
			break
		}
	}

    // Assign simName from attributes["simulation"]
    if sim, ok := payload.Attributes["simulation"].(string); ok {
        c.simName = sim
    }

    // Assign example from attributes["example"] (bool or string)
    if ex, ok := payload.Attributes["example"]; ok {
        switch v := ex.(type) {
        case bool:
            c.example = v
        case string:
            c.example = (strings.ToLower(v) == "true")
        }
    }

    // Assign logFormat from attributes["logformat"] (string)
    if lf, ok := payload.Attributes["logformat"].(string); ok {
        c.logFormat = lf
    }

    return c
=======
func parseFlags() cliCfg {
	var c cliCfg
	flag.StringVar(&c.projectFile,  "project-file",  "",     ".hms project file")
	flag.StringVar(&c.simName,      "sim-name",      "",     "simulation name")
	flag.StringVar(&c.excessPrecip, "excess-precip", "",     "path to export spatial excess precip as RAS .p##.tmp.hdf file or .dss file")
	flag.StringVar(&c.jsonFile,     "json-file",     "",     "configure HMS run with a JSON file based on the FFRD HMS schema")
	flag.BoolVar(&c.example,        "example",       false,  "run built-in example (tenk)")
	flag.StringVar(&c.logFormat,    "log-format",    "text", "text | json")
	flag.Parse()
	return c
>>>>>>> main
}

/* ---------- helpers ------------------------------------------------------ */

const jythonTpl = `from hms.model.JythonHms import *
from hms.model import Project
from hms.model.data import SpatialVariableType

from time import time

project_name = "%s"
project_dir = "%s"
sim_name = "%s"
excess_precip = "%s"

def _print(msg):
	print("Jython: " + str(msg))

# Open project, compute sim, save
project_path = project_dir + "/" + project_name + ".hms"
_print("opening project: " + project_path)
project = Project.open(project_path)
project.computeRun(sim_name)
_print("finished compute.")
project.saveAll()
_print("finished save.")

# Export excess precip if requested
if excess_precip:
	_print("exporting spatial excess precip to: " + excess_precip)
	spec = project.getComputeSpecification(sim_name)
	t1 = time()
	spec.exportSpatialResults(excess_precip, { SpatialVariableType.INC_EXCESS })
	t2 = time()
	_print("finished spatial excess precip export in " + str(t2 - t1) + " seconds.")
`

func buildJython(projectName, projectDir, simName string, excessPrecip string) (string, error) {
	tmp, err := os.CreateTemp("", "*.script")
	if err != nil {
		return "", err
	}
	code := fmt.Sprintf(jythonTpl, projectName, projectDir, simName, excessPrecip)
	if _, err = tmp.WriteString(code); err != nil {
		return "", err
	}

	println("Jython script:\n" + code)
	tmp.Close()
	return tmp.Name(), nil
}

func classifyAndLog(source, line string) {
	switch {
	case strings.Contains(line, "WARNING"):
		logWarn(source, line)
	case strings.Contains(line, "ERROR"):
		logError(source, line)
	case strings.Contains(line, "SEVERE"):
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

	configureLogger("text")

	// // Only use JSON file for configuration
	// if len(os.Args) < 2 {
	// 	fmt.Println("Usage: program <config.json>")
	// 	os.Exit(1)
	// }

    if len(os.Args) < 2 {
        fmt.Println("Usage: program <json-string>")
        os.Exit(1)
    }

	// jsonPath := os.Args[1]

	// payload, err := extractPayload(jsonPath)
	// if err != nil {
	// 	logError(hmsRunner, "cannot read JSON file: "+err.Error())
	// 	os.Exit(1)
	// }

	jsonInput := os.Args[1]

    var payload Payload
    if err := json.Unmarshal([]byte(jsonInput), &payload); err != nil {
        logError(hmsRunner, "cannot parse JSON string: "+err.Error())
        os.Exit(1)
    }

	// Map fields to variables
	name := payload.Name
	typeField := payload.Type
	attributes := payload.Attributes
	inputs := payload.Inputs
	outputs := payload.Outputs
	stores := payload.Stores

	// Log the mapped variables for debugging
	logInfo(hmsRunner, fmt.Sprintf("Name: %s, Type: %s", name, typeField))
	logInfo(hmsRunner, fmt.Sprintf("Attributes: %+v", attributes))
	logInfo(hmsRunner, fmt.Sprintf("Inputs: %+v", inputs))
	logInfo(hmsRunner, fmt.Sprintf("Outputs: %+v", outputs))
	logInfo(hmsRunner, fmt.Sprintf("Stores: %+v", stores))

	// print to verify
	println("Name: " + name)
	println("Type: " + typeField)
	println("Attributes: ")
	for k, v := range attributes {
		println(fmt.Sprintf("  %s: %v", k, v))
	}
	println("Inputs: ")
	for k, v := range inputs {
		println(fmt.Sprintf("  %s: %v", k, v))
	}
	println("Outputs: ")
	for k, v := range outputs {
		println(fmt.Sprintf("  %s: %v", k, v))
	}
	println("Stores: ")
	for k, v := range stores {
		println(fmt.Sprintf("  %s: %v", k, v))
	}

// <<<<<<< HEAD
	// map payload to a new var c
	c := populateCliCfgFromPayload(payload)
// =======
// 	var (
// 		hmsFile      string
// 		simName      string
// 		excessPrecip string
// 	)
// >>>>>>> main

	// // c, err := extractCliCfgFromPayload(jsonPath)
	// if err != nil {
	// 	logError(hmsRunner, "cannot read JSON file: "+err.Error())
	// 	os.Exit(1)
	// }
	// configureLogger(c.logFormat)

// <<<<<<< HEAD
	if c.projectFile == "" || !strings.HasSuffix(strings.ToLower(c.projectFile), ".hms") {
// =======
// 	case cfg.jsonFile != "":
// 		f, e := os.Open(cfg.jsonFile)
// 		if e != nil {
// 			logError(hmsRunner, "cannot read JSON file: "+e.Error())
// 			os.Exit(1)
// 		}
// 		type Schema struct {
// 			ProjectFile  string `json:"project_file"`
// 			SimName      string `json:"sim_name"`
// 			ExcessPrecip string `json:"excess_precip,omitempty"`
// 		}
// 		var s Schema
// 		if e = json.NewDecoder(f).Decode(&s); e != nil {
// 			logError(hmsRunner, "invalid JSON: "+e.Error())
// 			os.Exit(1)
// 		}
// 		hmsFile, simName, excessPrecip = s.ProjectFile, s.SimName, s.ExcessPrecip

// 	default:
// 		hmsFile, simName, excessPrecip = cfg.projectFile, cfg.simName, cfg.excessPrecip
// 	}

// 	if hmsFile == "" || !strings.HasSuffix(strings.ToLower(hmsFile), ".hms") {
// >>>>>>> main
		logError(hmsRunner, "project_file must be a .hms file")
		os.Exit(1)
	}
	if c.simName == "" {
		logError(hmsRunner, "sim_name is required")
		os.Exit(1)
	}
	rasHdfRe := regexp.MustCompile(`.*\.p[0-9][0-9]\.(hdf|tmp\.hdf)$`)
	if !rasHdfRe.MatchString(excessPrecip) &&
		!strings.HasSuffix(strings.ToLower(excessPrecip), ".dss") &&
		excessPrecip != "" {
		logError(hmsRunner, "excess_precip must be a .p##.tmp.hdf file or .dss file")
		os.Exit(1)
	}

	hmsHome := os.Getenv("HMS_HOME")

	// projectDir := filepath.Dir(c.projectFile)
	// projectName := strings.TrimSuffix(filepath.Base(c.projectFile), filepath.Ext(c.projectFile))

	// // projectDir := filepath.Dir(hmsFile)
	// projectDir = filepath.Dir(c.projectFile)
	// projectName = strings.TrimSuffix(filepath.Base(c.projectFile), filepath.Ext(c.projectFile))

	// // TODO: Have to figure out how to resolve local root from many potential Stores in json (hardcoding for testing)
	// projectDir := filepath.Join(root, c.projectFile)
	projectDir := filepath.Join("ffrd-trinity", c.projectFile)
	projectDir = filepath.Dir(projectDir)
	projectName := payload.Attributes["model-name"].(string)


	// --- build Jython script ---------------------------------------------
	scriptPath, e := buildJython(projectName, projectDir, simName, excessPrecip)
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

	logInfo(hmsRunner, fmt.Sprintf("Simulation '%s' completed for project '%s'.", c.simName, c.projectFile))
}

