library(plumber)

#* Log some information about the incoming request
#* @filter logger
function(req){
  cat(as.character(Sys.time()), "-",
      req$REQUEST_METHOD, req$PATH_INFO, "-",
      req$HTTP_USER_AGENT, "@", req$REMOTE_ADDR, "\n",
      req$HTTP_HOST)
  plumber::forward()
}

#* Manage CORS
#* @filter cors
function(req, res) {
  res$setHeader("Access-Control-Allow-Origin", "*")
  res$setHeader("Access-Control-Allow-Methods", "*")
  res$setHeader("Access-Control-Allow-Headers", "Content-Type")
  if (req$REQUEST_METHOD == "OPTIONS") {
    res$status <- 200 
    return (NULL)
  } else {
    plumber::forward()
  }
}

#* @filter setuser
function(req){
  un <- req$cookies$user
  req$username <- 'JMA'
  plumber::forward()
}

#* @filter checkAuth
function(req, res){
  if (is.null(req$username)){
    res$status <- 401 # Unauthorized
    return(list(error="Authentication required"))
  } else {
    plumber::forward()
  }
}

#* Return "hello world"
#* @get /hello
function(){
  "hello world"
}



