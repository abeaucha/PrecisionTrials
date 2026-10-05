#!/usr/bin/env Rscript
# ----------------------------------------------------------------------------
# gene_set_enrichment.R
# Authors: Antoine Beauchamp
# Created: September 30th, 2026

# Packages -------------------------------------------------------------------

suppressPackageStartupMessages(library(optparse))
suppressPackageStartupMessages(library(tidyverse))
suppressPackageStartupMessages(library(fgsea))


# Command line arguments -----------------------------------------------------

option_list <- list(
  make_option(
    "--ranks-file",
    type = "character"
    ),
  make_option(
    "--images-file",
    type = "character"
  ),
  make_option(
    "--mappings-file",
    type = "character",
    default = "knowledge/ReactomePathwayDatabase/Human_Reactome_June_01_2025_symbol.gmt"
  ),
  make_option(
    "--output-dir",
    type = "character"
  ),
  make_option(
    "--min-size",
    type = "numeric",
    default = 15
  ),
  make_option(
    "--max-size",
    type = "numeric",
    default = 500
    )
)


# Environment variables ------------------------------------------------------



# Functions ------------------------------------------------------------------

#' Import GMT file
#'
#' Modified version of the function from tmod, which currently doesn't work
#' in the package.
#'
#' @param file (character scalar) File to import (.gmt)
#'
#' @returns (list) Modules and genes.
importMsigDBGMT <- function(file) {
  # stop("This does not work at the present.")
  msig <- list()
  con <- file(file, open = "r")
  lines <- readLines(con)
  close(con)
  ids <- gsub("\t.*", "", lines)
  desc <- gsub("^[^\t]*\t([^\t]*)\t.*", "\\1", lines)
  genes <- gsub("^[^\t]*\t[^\t]*\t(.*)", "\\1", lines)
  msig$MODULES <- data.frame(ID = ids, Title = desc, stringsAsFactors = FALSE)
  if (any(duplicated(msig$MODULES$ID))) {
    warning("Duplicated IDs found; automatic IDs will be generated")
    msig$MODULES$oldID <- msig$MODULES$ID
    msig$MODULES$ID <- make.unique(as.character(msig$MODULES$ID))
  }
  rownames(msig$MODULES) <- msig$MODULES[, "ID"]
  msig$MODULES2GENES <- strsplit(genes, "\t")
  names(msig$MODULES2GENES) <- ids
  msig$GENES <- data.frame(ID = unique(unlist(msig$MODULES2GENES)))
  # msig <- new("tmod", msig)
  msig
}


# Main -----------------------------------------------------------------------

# Parse command line args
args <- parse_args(OptionParser(option_list = option_list))


# args <- list(
#   "ranks-file" = "tmp/AHBADecodingModule_correlations.csv",
#   "mappings-file" = "knowledge/ReactomePathwayDatabase/Human_Reactome_June_01_2025_symbol.gmt",
#   # "images-file" = "tmp/AHBADecodingModule_images.csv",
#   "output-dir" = "tmp/",
#   "min-size" = 15,
#   "max-size" = 500
# )

mappings <- importMsigDBGMT(file = args[["mappings-file"]])
pathways <- mappings$MODULES2GENES


mat_ranks <- read_csv(args[["ranks-file"]], show_col_types = FALSE) %>% 
  column_to_rownames("gene")

# df_images <- read_csv(args[["images-file"]], show_col_types = FALSE)


ranks_init <- mat_ranks[,1]
names(ranks_init) <- rownames(mat_ranks)
n_pathways <- nrow(fgsea(pathways = pathways,
                         stats = ranks_init,
                         minSize = args[["min-size"]], 
                         maxSize = args[["max-size"]]))

mat_ES <- matrix(data = 0, nrow = n_pathways, ncol = ncol(mat_ranks))
mat_NES <- matrix(data = 0, nrow = n_pathways, ncol = ncol(mat_ranks))
mat_pvals <- matrix(data = 0, nrow = n_pathways, ncol = ncol(mat_ranks))

colnames(mat_ES) <- paste0("X", 1:ncol(mat_ranks))
colnames(mat_NES) <- paste0("X", 1:ncol(mat_ranks))
colnames(mat_pvals) <- paste0("X", 1:ncol(mat_ranks))

# This is for one participant, using default gene resampling statistics
for (j in 1:ncol(mat_ranks)) {

ranks <- mat_ranks[,j]
names(ranks) <- rownames(mat_ranks)

fgsea_results <- fgsea(pathways = pathways,
                          stats = ranks,
                          # nproc = 
                          minSize = args[["min-size"]], 
                          maxSize = args[["max-size"]])

mat_ES[,j] <- fgsea_results[["ES"]]
mat_NES[,j] <- fgsea_results[["NES"]]
mat_pvals[,j] <- fgsea_results[["pval"]]

}

write_csv(x = as_tibble(mat_ES),
          file = file.path(args[["output-dir"]], "ES.csv"))

write_csv(x = as_tibble(mat_NES),
          file = file.path(args[["output-dir"]], "NES.csv"))

write_csv(x = as_tibble(mat_pvals),
          file = file.path(args[["output-dir"]], "pvals.csv"))

df_pathways <- mappings$MODULES %>% 
  as_tibble() %>% 
  semi_join(fgsea_results, by = c("ID" = "pathway")) %>% 
  rename(pathway = Title)

write_csv(x = df_pathways,
          file = file.path(args[["output-dir"]], "pathways.csv"))



