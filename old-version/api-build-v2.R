library(plumber)
library(Rook)

#* Log some information about the incoming request
#* @filter logger
function(req){
  
  cat(as.character(Sys.time()), "-",
      req$REQUEST_METHOD, req$PATH_INFO, "-",
      req$HTTP_USER_AGENT, "@", req$REMOTE_ADDR, "\n",
      req$SERVER_NAME, "\n",
      req$SERVER_PORT, "\n")
  
  plumber::forward()
  
}

#* @param req:[file]
#* @post /upload
function(req, res) {
  
  # Required for multiple file uploads
  names(req)
  
  # Parses into a Rook multipart file type;needed for API conversions
  fileInfo <- list(formContents = Rook::Multipart$parse(req))
  
  # This is where the file name is stored
  print(fileInfo$formContents$req$filename)
  file_name <- fileInfo$formContents$req$filename
  
  # The file is downloaded in a temporary folder
  tmpfile <- fileInfo$formContents$req$tempfile
  
  # Create a file path
  fn <- (paste0("data/zip/",file_name, sepp=''))
  
  #Copies the file into the designated folder
  file.copy(tmpfile, fn)
  
  res$body <- paste0("Your file is now stored in ", fn, "\n")
  res
  
}

#* @post /data
#* @param upload:file
function(upload) { 
  filename <- names(upload)
  content <- upload[[1]]
  writeBin(content, "data/zip/ciao.zip")
}

#* @get /index
function(req, res){
  include_file("index.html", res)
}

#' @get /get_data
#' @serializer contentType list(type='zip')
#' @param filename:[str]
function(filename) {
  dir_file <- file.path('data/zip', filename)
  content_file <- readBin(dir_file, 'raw', file.size(dir_file))
  as_attachment(content_file, filename)
}


