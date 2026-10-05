#!/usr/bin/env Rscript
# ----------------------------------------------------------------------------
# gene_set_enrichment.R
# Authors: Antoine Beauchamp
# Created: September 30th, 2026

# Packages -------------------------------------------------------------------

suppressPackageStartupMessages(library(optparse))
suppressPackageStartupMessages(library(tidyverse))

# Command line arguments -----------------------------------------------------

option_list <- list(
  make_option(
    "--genes-file",
        type = "character"
    ),
  make_option(
    "--mappings-file",
    type = "character"
  ),
  make_option(
    "--background-file",
    type = "character"
  ),
  make_option("--stringdb-score", type = "numeric", default = 950),
  make_option("--stringdb-version", type = "character", default = "12.0"),
)


# Environment variables ------------------------------------------------------



# Functions ------------------------------------------------------------------



# Main -----------------------------------------------------------------------


neighbourhood_k <- get_gene_neighbourhood(
      genes = ...,
      score = gene_score,
      stringdb_version = stringdb_version
    )
