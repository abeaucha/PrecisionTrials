

library(tidyverse)
library(fgsea)



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


correlations_file <- "AHBA_decoding_correlations.csv"
images_file <- "AHBA_decoding_image_files.csv"
mappings_file <- "knowledge/ReactomePathwayDatabase/Human_Reactome_June_01_2025_symbol.gmt"



data(examplePathways)
data(exampleRanks)

examplePathways

exampleRanks[1:10]

examplePathways[[1]] %in% names(exampleRanks)


df_correlations <- read_csv(correlations_file)

df_correlations


tmp <- gmtPathways(gmt.file = mappings_file)


mappings <- importMsigDBGMT(file = mappings_file)
pathways <- mappings$MODULES2GENES
dim(mappings$GENES)

genes <- df_correlations$gene

mat_correlations <- df_correlations %>% 
  column_to_rownames("gene")

ranks <- mat_correlations[,1]
names(ranks) <- genes


fgseaRes <- fgsea(pathways = pathways,
                  stats = ranks,
                  eps = 0.0, 
                  minSize = 15, maxSize = 500)

class(fgseaRes)

