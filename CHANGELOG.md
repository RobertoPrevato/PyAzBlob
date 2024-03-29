# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.0.6] - 2022-08-14 :fish:
- Corrects bug when the input path starts with "./"

## [0.0.5] - 2022-08-13 :fish:
- Adds a change log
- Upgrades dependencies
- Disables the file log by default, unless an environment variable is specified:
  `PYAZBLOB_FILE_LOG=true` | `PYAZBLOB_FILE_LOG=TRUE`
- Enforces `black`, `isort` in the build job
- Publishes to PyPi through GitHub Actions
