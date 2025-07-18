General Container Specification
========================

# Introduction
Explain the utility of the container and the context within which it is expected to be used.

# Build Instructions
Instructions on how to build the container and what adjacent data is expected to be present alongside the Dockerfile.

# Usage
Further details on the embedded utilities, other software dependencies, etc.

# Inputs/Outputs
The required (and optional) inputs/outputs for each feature of the container should be described and examples provided to further clarify usage.

# Container Specification Template
Drawing from the [BioContainers Spec](https://github.com/BioContainers/specs/blob/master/container-specs.md), a metadata standard is proposed to compliment this readme file. Container metadata further supports FAIR principals and ensures the resource is discoverable, versioned, self-documenting, and aids reproducibility. For example:

| Field          | Description | Optional                                             | Example   |
|----------------|------------ |------------------------------------------------------|-----------|
| LABEL base_image            | The original image where the software has been built | **Mandatory** | base_image=" biodckr/biodocker" |
| LABEL version               | Version of the tool's Dockerfile                     | **Mandatory** | version="2" |
| LABEL software.version      | Version of the software or tool                      | **Mandatory** | software.version="2015020"     |
| LABEL software              | Name of the software or tool                         | **Mandatory** | software="Comet"               |
| LABEL about.summary         | A short description of the software or tool.         | **Mandatory** | about.summary="Peptide" identification|
| LABEL about.home            | The original software website.                       | **Mandatory** | about.home="http://comet-ms.sourceforge.net/"  |
| LABEL about.documentation   | URL(s) containing information about software         | _Optional_  | about.documentation="http://comet-ms.sourceforge.net/"     |
| LABEL about.license         | SPDX license specification. If not in the SPDX list, specify URL in license_file> | **Mandatory** | about.license="SPDX:Apache-2.0"          |
| LABEL about.license_file    | License path location in the container or url (according to license requirements) | _Optional_ |         |  
| LABEL about.tags            | Tags about the software that enable to find and classify the software tool.| _Optional_ | about.tags="proteomics, mass spectrometry, biocontainers"       |
| LABEL maintainer | The developer in charge of the container/software | **Mandatory** | maintainer="Yasset Perez-Riverol <yperez@ebi.ac.uk>" |
| LABEL extra.identifiers  | Extra identifiers are external identifiers in other resources that will allow to pull metadata, an external information from other resources (e.g biotools). In order to be compatible with Docker specification the domain (database) of the identifiers should be specified in the name of the label. | _Optional_ | extra.identifiers.biotools=abyss |  


## Dockerfile example:

```Dockerfile
# Base Image
FROM biocontainers/biocontainers:latest

# Metadata
LABEL base_image="biocontainers:latest" \
      version="3"   \
      software="Comet" \
      software.version="2016012" \
      about.summary="an open source tandem mass spectrometry sequence database search tool" \
      about.home="http://comet-ms.sourceforge.net/" \
      about.documentation="http://comet-ms.sourceforge.net/parameters/parameters_2016010/" \
      about.license="SPDX:Apache-2.0" \
      about.license_file="/usr/share/common-licenses/Apache-2.0" \
      about.tags="Proteomics" \
      extra.identifiers.biotools=comet

# Maintainer
LABEL maintainer="Felipe da Veiga Leprevost <felipe@leprevost.com.br>"

USER biodocker

RUN ZIP=comet_binaries_2016012.zip && \
  wget https://github.com/BioDocker/software-archive/releases/download/Comet/$ZIP -O /tmp/$ZIP && \
  unzip /tmp/$ZIP -d /home/biodocker/bin/Comet/ && \
  chmod -R 755 /home/biodocker/bin/Comet/* && \
  rm /tmp/$ZIP

RUN mv /home/biodocker/bin/Comet/comet_binaries_2016012/comet.2016012.linux.exe /home/biodocker/bin/Comet/comet

ENV PATH /home/biodocker/bin/Comet:$PATH

WORKDIR /data/

```
