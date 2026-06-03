# API build

library(plumber)
library(jsonlite)
library(dplyr)

# Users
# path <- '~/1. Projects/3. RProject/PlumbeR/'
# df_users <- read.table(paste0(path,'ip_authorized.txt'), sep = '\t', header = T)

# Sql
# api_db <- DBI::dbConnect(RSQLite::SQLite(), '~/1. Projects/3. RProject/PlumbeR/API_DB.db')


# Functions ---------------------------------------------------------------

# css
css <- function(req, res) {
  paste(readLines("styles.css"), collapse = '')
}

# js
js <- function(req, res) {
  paste(readLines("script.js"), collapse = '')
}

# Main
home_page <- function(req, res) {
  paste(readLines("index.html"), collapse = '')
}

# Page 1
page1 <- function(req, res) {
  paste(readLines("solicitud.html"), collapse = '')
}

# Page 2
page2 <- function(req, res) {
  paste(readLines("Bandeja.html"), collapse = '')
}

# Page 3
page3 <- function(req, res) {
  paste(readLines("Bandeja1.html"), collapse = '')
}

# Authentication
auth <- function(req, res) {
  # Users
  path <<- '~/1. Projects/3. RProject/PlumbeR/'
  df_users <<- read.table(paste0(path,'ip_authorized.txt'), sep = '\t', header = T)
  user <<- dplyr::filter(df_users, ip==req$REMOTE_ADDR)
  
  # Log
  df_log <- data.frame(date = format(Sys.time(), '%Y-%m-%d %H:%M:%S'), ip=req$REMOTE_ADDR, status=res$status)
  write.table(df_log, file = 'ip_logs.txt', append = TRUE, row.names = F, col.names = F)
  # Hist
  df_histor <- read.table(paste0(path,'ip_logs.txt'), sep = ' ', header = F, stringsAsFactors = F)
  names(df_histor) <- c('datetime', 'ip', 'status')
  d_eval <- lubridate::ymd_hms(Sys.time()-(60*60))
  df_histor <- dplyr::filter(df_histor, ip==req$REMOTE_ADDR & lubridate::ymd_hms(datetime) >= d_eval)
  
  # Response
  if (is.na(user[1,2])) {
    authhtml <- sprintf('<p> Authentication required: %s </p>', req$REMOTE_ADDR)
    res$status <- 401 # Unauthorized
    return(authhtml)
  } else if (nrow(df_histor) > 1000) {
    authhtml <- sprintf('<p> Demasiadas solicitudes de esta IP: %s </p>', req$REMOTE_ADDR)
    res$status <- 429
    return(authhtml)
  } else {
    plumber::forward()
  }
}

# Welcome
welcome <- function(req, res) {
  userjson <- toJSON(list(username = user[1,2]), auto_unbox = TRUE)
  return(userjson)
}

# Tramite Normal --------------------------------------------------------------------------------------------------

# Consulta TN
get_tn <- function(req, res) {
  jsonData <- req$postBody
  data <- fromJSON(jsonData)
  dni <- gsub('[^0-9]', '', data$CODDOC)
  path_db <- '~/1. Projects/3. RProject/PlumbeR/API_DB.db'
  
  # Result
  if (stringr::str_length(dni)==8) {
    api_db <- DBI::dbConnect(RSQLite::SQLite(), path_db)
    tipoDoc <- ifelse(data$TIPODOC=='DNI', 1, 2)
    codDoc <- data$CODDOC
    
    v_names <- c('TIPDOC','CODDOC','Resolución','Marca Cliente','Segmento','Perfil PLD',
                 'TEA Campaña','CCF Campaña','Ingreso Eval.','Cuota SSFF','IFIS','Oferta 48m',
                 'Tipo Oferta','OFERTA_PLD_5_INI','SALDO_CONSUMO','Edad','Inmueble',
                 'Departamento','Provincia','Distrito','Zona',
                 'TEM Campaña','Cuota 48m','RCI Eval.')
    
    df_clie <- DBI::dbGetQuery(
      conn = api_db, 
      statement = sprintf(
        "select * from CampaniaPLD where TIPDOC = %i and CODDOC = '%s'", tipoDoc, codDoc)
      )
    
    if (nrow(df_clie) > 0) {
      df <- dplyr::mutate(df_clie, TEM = (1+(TASA_PLD/100))^(1/12)-1)
      df <- dplyr::mutate(df, CUOTA_48M = round(TEM*OFERTA_PLD_48/(1-(1+TEM)^(-48)), 2))
      df <- dplyr::mutate(df, RCI = round(GASTO/INGRESO_EVAL_PLD, 4)*100)
      df <- dplyr::mutate(df, AGRUP_ZONA = stringr::str_to_upper(AGRUP_ZONA))
      df <- dplyr::mutate_at(df, vars(INGRESO_EVAL_PLD, GASTO, OFERTA_PLD_48, CUOTA_48M), ~format(round(.,2), big.mark=","))
      df <- dplyr::mutate_at(df, vars(TASA_PLD, CCF_PLD, RCI), ~scales::percent(./100, accuracy = 0.1))
      df <- dplyr::mutate(df, FLG_INMUEBLE = ifelse(FLG_INMUEBLE==1, 'SI', 'NO'))
      df <- dplyr::mutate(df, CLUSTER = paste('PERFIL', CLUSTER))
      df <- dplyr::rename_all(df, ~v_names)
      df$nrow <- 1:nrow(df)
      df$Acción <- sprintf('<a href="#" onclick="Validate(%i)">Evaluar</a>', df$nrow)
    } else {
      df <- data.frame(Identidad = as.integer())
    }
    
    if (nrow(df)==0) {
      response <- list(Error = "Cliente no encontrado")
    } else {
      response <- list(
        data1 = dplyr::select(df, `Marca Cliente`, `Segmento`, `Perfil PLD`, `Inmueble`),
        data2 = dplyr::select(df, `Ingreso Eval.`, `Cuota SSFF`, `IFIS`, `Edad`),
        data3 = dplyr::select(df, `Departamento`, `Provincia`, `Distrito`, `Zona`),
        data4 = dplyr::select(df, `Tipo Oferta`, Resolución, `Oferta 48m`, `Cuota 48m`,
                              `TEA Campaña`, `CCF Campaña`, `RCI Eval.`, Acción))
    }
    
  } else {
    response <- list(Error = "Verificar DNI")
  }
  
  # Guarda consulta
  if (nrow(df) > 0) {
    df_clie$FECHA_CONSULTA <- as.character(Sys.Date())
    df_clie$HORA_CONSULTA <- format(Sys.time(), '%H:%M:%S')
    df_clie$USUARIO <- user[1,2]
    
    # Write db
    DBI::dbWriteTable(api_db, 'BaseConsultasTN', df_clie, append = TRUE)
  }
  
  # Response
  DBI::dbDisconnect(api_db)
  return(response)
}

# Consulta TN: Validacion
validate1 <- function(req, res) {
  jsonData <- req$postBody
  data <- fromJSON(jsonData)
  df <- data.frame(data)
  
  tipoDoc <- ifelse(data$TIPODOC=='DNI', 1, 2)
  codDoc <- data$CODDOC
  
  path_db <- '~/1. Projects/3. RProject/PlumbeR/API_DB.db'
  api_db <- DBI::dbConnect(RSQLite::SQLite(), path_db)
  
  df_clie <- DBI::dbGetQuery(
    conn = api_db, 
    statement = sprintf(
      "select MARCA_CLIENTE, AGR_SITLAB_SUN, CLUSTER, INGRESO_EVAL_PLD, FLG_INMUEBLE
         from CampaniaPLD where TIPDOC = %i and CODDOC = '%s'", 
      tipoDoc, codDoc))
  
  if (nrow(df_clie) > 0) {
    df_clie$FLG_SUNEDU <- ifelse(substr(df_clie$AGR_SITLAB_SUN, 1, 2) == 'CS', 'CON SUNEDU', 'SIN SUNEDU')
    df_clie$CLUSTER <- paste('PERFIL', df_clie$CLUSTER)
    
    # Bind
    df <- dplyr::bind_cols(df, df_clie)
    
    response <- list(
      Campaña = df$Oferta,
      `Tipo Doc.` = data$TIPODOC,
      Documento = codDoc,
      `Marca Cliente` = df_clie$MARCA_CLIENTE,
      `Perfil PLD` = df_clie$CLUSTER,
      `Marca Sunedu` = df_clie$FLG_SUNEDU,
      `Sit. Laboral` = '<select id="SitLaboral">
                          <option value="DEP">DEP</option>
                          <option value="INDEP">INDEP</option>
                          <option value="INFORMAL">INFORMAL</option>
                        </select>',
      `Carga Financ.` = '<input type="text" id="Deuda" name="Deuda" placeholder="Opcional">',
      `Ingreso Val.` = '<input type="text" id="Ingreso" name="Ingreso">'
    )
  } else {
    response <- list(Error = "Verificar DNI")
  }
  
  DBI::dbDisconnect(api_db)
  return(response)
}

# Consulta TN: Actualiza oferta
validate2 <- function(req, res) {
  jsonData <- req$postBody
  data <- fromJSON(jsonData)
  
  df <- data.frame(data)
  # df$CODDOC <- stringr::str_pad(df$CODDOC, width = 8, pad = '0')
  df$Ingreso <- as.numeric(df$Ingreso)
  df$Deuda <- as.numeric(df$Deuda)
  df$Periodo <- as.integer(format(Sys.Date(), '%Y%m'))
  df$FechaEvaluacion <- as.character(Sys.Date())
  df$HoraEvaluacion <- format(Sys.time(), '%H:%M:%S')
  df$UserEvaluacion <- user[1,2]
  df$Registro <- 1
  
  path_db <- '~/1. Projects/3. RProject/PlumbeR/API_DB.db'
  api_db <- DBI::dbConnect(RSQLite::SQLite(), path_db)
  
  tipoDoc <- ifelse(df$TIPODOC=='DNI', 1, 2)
  codDoc <- df$CODDOC
  
  df_clie <- DBI::dbGetQuery(
    conn = api_db, 
    statement = sprintf(
      "select GASTO, OFERTA_PLD_5_INICIAL, SALDO_CONSUMO, TASA_PLD 
         from CampaniaPLD where TIPDOC = %i and CODDOC = '%s'", 
      tipoDoc, codDoc)
  )
  
  # Oferta PLD
  sheets <- openxlsx::getSheetNames('ParametrosPLD-v3.xlsx')
  ls_param_pld <- lapply(sheets, openxlsx::read.xlsx, xlsxFile = 'ParametrosPLD-v3.xlsx')
  names(ls_param_pld) <- sheets
  
  # data.table::fwrite(df, file = '~/1. Projects/3. RProject/PlumbeR/test.txt')
  # df <- data.table::fread(file = '~/1. Projects/3. RProject/PlumbeR/test.txt')
  
  if (nrow(df) > 0) {
    # Oferta PLD
    df <- df |>
      dplyr::bind_cols(df_clie) |>
      dplyr::mutate(
        perfil = as.integer(gsub('[^0-9]', '', Perfil)),
        rng_ingreso = cut(Ingreso, breaks=c(-Inf,1000,2000,3000,4000,5000,7000,Inf), labels=F)-1,
        marca_cliente_cm = ifelse(Cliente == 'NO CLIENTE', 0, 1),
        sitlab_sun = paste0(ifelse(Sunedu=='CON SUNEDU','CS','SS'),'_',ifelse(Sueldo=='DEP','DEP','INDEP')),
        tea_pld_48 = ifelse(perfil==1, 0.3, ifelse(perfil==2, 0.35, 0.4)),
        tem_pld_48 = exp(log(1 + tea_pld_48)/12)-1,
        pef_pld = ifelse(is.na(Deuda), GASTO, Deuda)/Ingreso
      ) |>
      dplyr::left_join(
        ls_param_pld$ParamPLD,
        by = c('perfil', 'rng_ingreso')
      ) |>
      dplyr::left_join(
        ls_param_pld$NVI,
        by = c('perfil', 'rng_ingreso', 'sitlab_sun', 'marca_cliente_cm')
      ) |>
      dplyr::mutate(
        oferta_1 = round((Ingreso*(param_pld-pef_pld))*(1-(1/(1+tem_pld_48)^(plazo)))/tem_pld_48, 2),
        oferta_2 = Ingreso * multip_nvi
      ) |>
      dplyr::left_join(
        ls_param_pld$Oferta3,
        by = c("marca_cliente_cm", "perfil", "sitlab_sun", "rng_ingreso")
      ) |> 
      dplyr::left_join(
        ls_param_pld$TopeGarita,
        by = c("perfil", "sitlab_sun")
      ) |> 
      dplyr::mutate(
        oferta_pld_ini = pmin(oferta_1, oferta_2, oferta_3),
        oferta_5 = ifelse(OFERTA_PLD_5_INICIAL <= tope_garita, tope_garita, OFERTA_PLD_5_INICIAL),
        oferta_6 = oferta_5 - SALDO_CONSUMO,
        max_tope_min_6 = pmax(tope_garita, oferta_6),
        oferta_pld = round(
          ifelse(oferta_pld_ini < tope_garita, oferta_pld_ini, pmin(oferta_pld_ini, max_tope_min_6)), -2),
        oferta_pld = pmax(oferta_pld, 0),
        tem_camp = (1+(TASA_PLD/100))^(1/12)-1,
        tem_eval = ifelse(is.na(tem_camp), tem_pld_48, tem_camp),
        cuota_camp = round(tem_eval*oferta_pld/(1-(1+tem_eval)^(-plazo)),0)
      )
    
    # Response
    response <- list(
      data1 = data.frame(
        `Segmento cliente` = df$sitlab_sun,
        `Ingreso Revisado` = format(round(df$Ingreso, 2), big.mark=","),
        `Nuevo RCI` = scales::percent(df$pef_pld, accuracy = 0.1),
        `Nueva Oferta` = format(round(df$oferta_pld, 2), big.mark=","), 
        `Cuota Oferta` = format(df$cuota_camp, big.mark=","),
        `Tasa Oferta` = scales::percent(df$TASA_PLD/100, accuracy = 0.1),
        `Plazo Oferta` = df$plazo,
        check.names = F),
      # alerta1 = ifelse(df$Ingreso < 2000, 'Alerta: Ingresos menores a 2,000', ''),
      # alerta2 = ifelse(df$oferta_pld < 3000, 'Alerta: Oferta menor a 3,000', ''),
      # alerta3 = ifelse(df$pef_pld > 0.5, 'Alerta: RCI mayor a 50%', ''),
      data2 = data.frame(
        `Tipo Doc.` = df$TIPODOC,
        Documento = codDoc,
        Campaña = df$Oferta,
        `Monto Solicitado` = '<input type="text" id="Solicitado" name="Solicitado">',
        Comentario = '<textarea type="text" id="Comentario" style="height: 100px; width: 250px;"></textarea>',
        check.names = F)
    )
  } else {
    response <- list(Error = "Verificar DNI")
  }
  
  # Graba evaluacion
  if (nrow(df) > 0) {
    # Ordena
    df <- dplyr::select(df, Periodo, dplyr::everything())
    df <- dplyr::relocate(df, Registro, .after = cuota_camp)
    df <- dplyr::select(df, -perfil)
    
    # Anula anteriores
    DBI::dbClearResult(
      DBI::dbSendQuery(
      conn = api_db, 
      statement = sprintf(
        "update BaseValidacion
            set Registro = 9
          where Periodo = %i;", 
        df$Periodo))
    )
    
    DBI::dbWriteTable(api_db, 'BaseValidacion', df, append = TRUE)
    response <- c(response, list(respuesta = 'Proceso exitoso.'))
  }
  
  DBI::dbDisconnect(api_db)
  return(response)
}

# Consulta TN: Graba solicitud
grabasol <- function(req, res) {
  jsonData <- req$postBody
  data <- fromJSON(jsonData)
  
  df <- data.frame(data)
  df$Monto <- format(as.numeric(df$Monto), big.mark=",")
  df$FechaSolicitud <- as.character(Sys.Date())
  df$HoraSolicitud <- format(Sys.time(), '%H:%M:%S')
  df$UserSolicitud <- user[1,2]
  df$Estado <- 'Enviada'
  df$Registro <- 1L
  
  df <- dplyr::relocate(df, Comentario, .after = Registro)
  
  # data.table::fwrite(df, file = '~/1. Projects/3. RProject/PlumbeR/test2.txt')
  # df <- data.table::fread(file = '~/1. Projects/3. RProject/PlumbeR/test2.txt')
  # df$CODDOC <- stringr::str_pad(df$CODDOC, width = 8, pad = '0')
  
  path_db <- '~/1. Projects/3. RProject/PlumbeR/API_DB.db'
  api_db <- DBI::dbConnect(RSQLite::SQLite(), path_db)
  
  # Check solicitudes
  v_sol <- DBI::dbGetQuery(
    conn = api_db,
    statement = sprintf(
      "select max(FechaSolicitud) from BaseSolicitudesTN
        where TIPODOC = '%s' and CODDOC = '%s' and REGISTRO = 1",
      df$TIPODOC, df$CODDOC))[[1]]
  
  # Controles
  response <- list(respuesta = '')
  
  if (is.na(v_sol)) {v_sol <- '2020-01-01'}
  if (as.integer(format(as.Date(v_sol),'%Y%m')) == as.integer(format(Sys.Date(),'%Y%m'))) {
    response <- list(respuesta = 'Error: ya existe una solicitud para el periodo en curso.')
  }
  
  if (substr(response$respuesta, 1, 5) != 'Error' & df$Sueldo == 'INFORMAL') {
    response <- list(respuesta = 'Error: Fuente de ingresos informal.')
  }
  
  if (substr(response$respuesta, 1, 5) != 'Error' & as.numeric(sub(",", "", df$Ingreso)) < 2000) {
    response <- list(respuesta = 'Error: Ingreso menor a 2,000.')
  }
  
  if (substr(response$respuesta, 1, 5) != 'Error' & as.numeric(sub("%", "", df$RCI))/100 > 0.5) {
    response <- list(respuesta = 'Error: RCI mayor a 50%.')
  }
  
  if (substr(response$respuesta, 1, 5) != 'Error' & as.numeric(sub(",", "", df$Oferta)) < 3000) {
    response <- list(respuesta = 'Error: Oferta menor a 3,000.')
  }
  
  if (substr(response$respuesta, 1, 5) != 'Error' 
      & as.numeric(sub(",", "", df$Monto)) > as.numeric(sub(",", "", df$Oferta))) {
    response <- list(respuesta = 'Error: Monto solicitado mayor a Oferta.')
  }
  
  if (substr(response$respuesta, 1, 5) != 'Error' & (is.na(df$Comentario) | df$Comentario == '')) {
    response <- list(respuesta = 'Error: Ingrese un comentario.')
  }
  
  if (response$respuesta == '') {
    DBI::dbWriteTable(api_db, 'BaseSolicitudesTN', df, append = TRUE)
    response <- list(respuesta = 'SOLICITUD REGISTRADA.')
  }
  
  DBI::dbDisconnect(api_db)
  return(response)
}

# Consulta TN: Bandeja
bandejasol <- function(req, res) {
  jsonData <- req$postBody
  data <- fromJSON(jsonData)
  
  df_users2 <<- read.table(paste0(path,'ip_evaluator.txt'), sep = '\t', header = T)
  user2 <<- dplyr::filter(df_users2, ip==req$REMOTE_ADDR)
  
  path_db <- '~/1. Projects/3. RProject/PlumbeR/API_DB.db'
  api_db <- DBI::dbConnect(RSQLite::SQLite(), path_db)
  
  v_date <- format(lubridate::ymd(paste0(data$Periodo,'01')), '%Y-%m-%d')
  
  df_sol <- DBI::dbGetQuery(
    conn = api_db, 
    statement = sprintf(
      "select * from BaseSolicitudesTN where FechaSolicitud >= %s and Registro = 1", 
      v_date))
  
  if (nrow(df_sol) > 0) {
    df_sol <- dplyr::select(df_sol, -TIPODOC, -Registro, -Sueldo, -Comentario, -HoraSolicitud)
    df_sol$nrow <- 1:nrow(df_sol)
    df_sol$test <- ifelse(df_sol$Estado != 'Enviada', 1, 0)
    df_sol$Reverso <- ifelse(df_sol$test==0, 
                             sprintf('<a id="Reverso" href="#" onclick="AnulaSolTN(%i)">Anular</a>', df_sol$nrow),
                             '<a id="Reverso">Anular</a>')
    df_sol$test2 <- ifelse(df_sol$UserSolicitud==user2[1,2], 
                           sprintf('href="#" onclick="ShowUpdateSolTN(%i)"', df_sol$nrow), '')
    df_sol$Estado <- sprintf('<div> 
                                <a id="Estado" %s> %s </a>
                                <div id="UpdateSol%i" style="display: none;">
                                  <select id="EstadoUP%i">
                                    <option value="Enviada">Enviada</option>
                                    <option value="Aprobada">Aprobada</option>
                                    <option value="Observada">Observada</option>
                                    <option value="Rechazada">Rechazada</option>
                                  </select>
                                  <input type="submit" value="Registrar" onclick="UpdateSolTN(%i)">
                                  <p id="ResEstadoUP%i"></p>
                                </div>
                             </div>', 
                             df_sol$test2,
                             df_sol$Estado,
                             df_sol$nrow,
                             df_sol$nrow,
                             df_sol$nrow,
                             df_sol$nrow)
    df_sol <- dplyr::rename_at(df_sol, vars(FechaSolicitud, UserSolicitud), ~c('FechaSol','UserSol'))
    df_sol <- dplyr::select(df_sol, Reverso, dplyr::everything())
    df_sol <- dplyr::relocate(df_sol, Estado, .after = Reverso)
    df_sol <- dplyr::relocate(df_sol, Monto, .after = Oferta)
    df_sol <- dplyr::rename_at(df_sol, vars(CODDOC), ~c('DNI'))
    df_sol$nrow <- NULL
    df_sol$test <- NULL
    df_sol$test2 <- NULL
  } else {
    df_sol <- data.frame(Periodo = data$Periodo, Campaña = 'No se encontraron solicitudes')
  }
  
  # Response
  response <- list(data1 = df_sol)

  DBI::dbDisconnect(api_db)
  return(response)
}

# Bandeja 2: Reverso
anulasol <- function(req, res) {
  jsonData <- req$postBody
  data <- fromJSON(jsonData)
  
  path_db <- '~/1. Projects/3. RProject/PlumbeR/API_DB.db'
  api_db <- DBI::dbConnect(RSQLite::SQLite(), path_db)
  
  DBI::dbClearResult(DBI::dbSendQuery(
    conn = api_db, 
    statement = sprintf(
      "update BaseSolicitudesTN set Registro = 9 
        where Registro = 1 and CODDOC = '%s' and FechaSolicitud = '%s'", 
      data$CODDOC, data$FechaSol)))
  
  response <- sprintf('%s Solicitud anulada: %s (%s)', 
                      Sys.Date(), data$Campaña, data$CODDOC)
  
  DBI::dbDisconnect(api_db)
  return(response)
}

# Bandeja 2: Update
updatesol <- function(req, res) {
  jsonData <- req$postBody
  data <- fromJSON(jsonData)
  
  path_db <- '~/1. Projects/3. RProject/PlumbeR/API_DB.db'
  api_db <- DBI::dbConnect(RSQLite::SQLite(), path_db)
  
  DBI::dbClearResult(DBI::dbSendQuery(
    conn = api_db, 
    statement = sprintf(
      "update BaseSolicitudesTN set Estado = '%s' 
        where Registro = 1 and CODDOC = '%s' and FechaSolicitud = '%s'", 
      data$EstdoUP, data$CODDOC, data$FechaSol)))
  
  response <- 'Proceso Exitoso.'
  
  DBI::dbDisconnect(api_db)
  return(response)
}

# Load zip file
upload_file <- function(req, res) {
  fileInfo <- list(formContents = Rook::Multipart$parse(req))
  print(fileInfo$formContents$req$filename)
  file_name <- fileInfo$formContents$req$filename
  tmpfile <- fileInfo$formContents$req$tempfile
  fn <- (paste0("data/zip/", file_name, sepp=''))
  file.copy(tmpfile, fn)
  res$body <- paste0("File guardado en ", fn, "\n")
  return(res)
}

# Download zip file
download_file <- function(filename) {
  dir_file <- file.path('data/zip', filename)
  if (file.exists(dir_file)) {
    content_file <- readBin(dir_file, 'raw', file.size(dir_file))
    as_attachment(content_file, filename)
  }
}


# Cobranzas -------------------------------------------------------------------------------------------------------

# Consulta cob
get_data <- function(req, res) {
  jsonData <- req$postBody
  data <- fromJSON(jsonData)
  dni <- gsub('[^0-9]', '', data$CODDOC)
  path_db <- '~/1. Projects/3. RProject/PlumbeR/API_DB.db'
  
  # Result
  if (stringr::str_length(dni)==8) {
    api_db <- DBI::dbConnect(RSQLite::SQLite(), path_db)
    tipoDoc <- data$TIPODOC
    codDoc <- data$CODDOC
    
    id <- as.integer(paste0(ifelse(tipoDoc=='DNI', 1, 2), codDoc))
    
    df_clie <- DBI::dbGetQuery(
      conn = api_db, 
      statement = sprintf('select * from BaseClientes where Identidad = %s', id))
    
    df_rcc <- DBI::dbGetQuery(
      conn = api_db, 
      statement = sprintf("select * from BaseRCC where CODDOC = '%s'", codDoc))
    
    df_camp <- DBI::dbGetQuery(
      conn = api_db, 
      statement = sprintf("select * from BaseOferta where Identidad = %s", id))
    
    if (nrow(df_rcc)==0) {
      df_rcc <- data.frame(
        TIPDOC = ifelse(tipoDoc=='DNI', 1, 2), CODDOC = codDoc, PEF_PLD = as.double(NA))
    }
    
    if (nrow(df_clie) > 0) {
      df <- dplyr::bind_cols(df_clie, df_rcc)
      df <- dplyr::mutate(df, SaldoPrincipal = format(SaldoPrincipal, big.mark=","))
      df <- dplyr::mutate(df, FechaCredito = lubridate::ymd(df_clie$FechaApertura))
      df <- dplyr::mutate(df, TasaGastos = scales::percent(TasaGastos/100, accuracy = 0.1))
      df <- dplyr::mutate(df, RCI = scales::percent(PEF_PLD, accuracy = 0.1))
      df <- dplyr::mutate(df, DiasMora = pmax(DiasMora, 0))
    } else {
      df <- data.frame(Identidad = as.integer())
    }
    
    if (nrow(df_camp) > 0) {
      df_camp <- dplyr::mutate_at(df_camp, vars(DctoCapital:DctoICV), ~scales::percent(.))
      df_camp$FechaConsulta <- Sys.Date()
      df_camp$nrow <- 1:nrow(df_camp)
      # df_camp$Solicitud <- sprintf('<a href="#" onclick="EnviaSol(%i)">Enviar</a>', df_camp$nrow)
      df_camp$Solicitud <- '<a href="/Solicitud">Enviar</a>'
      df_camp$nrow <- NULL
    } else {
      df_camp <- data.frame(Identidad = id, Campaña = 'Cliente no cuenta con campañas')
    }
    
    if (nrow(df)==0) {
      response <- list(Error = "Cliente no encontrado", data3 = dplyr::select(df_camp, -Identidad))
    } else {
      response <- list(
        Documento = codDoc,
        Cuenta = df_clie$Cuenta, 
        Cartera = df_clie$Cartera,
        Producto = df_clie$CodigoProducto,
        data1 = dplyr::select(df, FechaCredito, Desembolso=SaldoPrincipal, CuotasPactadas, CuotasPagadas),
        data2 = dplyr::select(df, SaldoPrincipal, DiasMora, TEA=TasaGastos, RCI),
        data3 = dplyr::select(df_camp, -Identidad))
    }
    
  } else {
    response <- list(Error = "Verificar DNI")
  }
  
  # Guarda consulta
  if (nrow(df) > 0) {
    df_final <- dplyr::bind_cols(df_clie, df_rcc)
    df_final <- dplyr::left_join(df_final, df_camp, by = 'Identidad')
    df_final$FechaConsulta <- as.character(Sys.Date())
    df_final$Solicitud <- NULL
    df_final$HoraConsulta <- format(Sys.time(), '%H:%M:%S')
    df_final$Usuario <- user[1,2]
    
    # Write db
    DBI::dbWriteTable(api_db, 'BaseConsultas', df_final, append=TRUE)
  }
  
  # Response
  DBI::dbDisconnect(api_db)
  return(response)
}

# Solicitud 1: Consulta
envio_sol1 <- function(req, res) {
  jsonData <- req$postBody
  data <- fromJSON(jsonData)
  dni <- gsub('[^0-9]', '', data$CODDOC)
  path_db <- '~/1. Projects/3. RProject/PlumbeR/API_DB.db'
  
  if (stringr::str_length(dni)==8) {
    api_db <- DBI::dbConnect(RSQLite::SQLite(), path_db)
    tipoDoc <- data$TIPODOC
    codDoc <- data$CODDOC
    
    id <- as.integer(paste0(ifelse(tipoDoc=='DNI', 1, 2), codDoc))
    
    df_camp <- DBI::dbGetQuery(
      conn = api_db, 
      statement = sprintf("select * from BaseOferta where Identidad = %s", id))
    
    if (nrow(df_camp) > 0) {
      df_camp <- dplyr::mutate_at(df_camp, vars(DctoCapital:DctoICV), ~scales::percent(.))
      df_camp$FechaConsulta <- Sys.Date()
      df_camp$nrow <- 1:nrow(df_camp)
      df_camp$Solicitud <- sprintf('<a href="#" onclick="EnviaSol(%i)">Enviar</a>', df_camp$nrow)
      df_camp$nrow <- NULL
      # df_camp$TIPDOC <- ifelse(substr(df_camp$Identidad, 1, 1)==1, 'DNI',  'CEX')
      # df_camp$CODDOC <- substring(df_camp$Identidad, 2)
      df_camp$Identidad <- NULL
      # df_camp <- dplyr::select(df_camp, TIPDOC, CODDOC, dplyr::everything())
    } else {
      df_camp <- data.frame(Identidad = id, Campaña = 'Cliente no cuenta con campañas')
    }
    
    response <- list(data1 = df_camp)
    
  } else {
    response <- list(Error = "Verificar DNI")
  }
  
  # Response
  DBI::dbDisconnect(api_db)
  return(response)
}

# Solicitud 2: Resumen
envio_sol2 <- function(req, res) {
  jsonData <- req$postBody
  data <- fromJSON(jsonData)
  df <- data.frame(data)
  
  tipoDoc <- data$TIPODOC
  codDoc <- data$CODDOC
  
  path_db <- '~/1. Projects/3. RProject/PlumbeR/API_DB.db'
  api_db <- DBI::dbConnect(RSQLite::SQLite(), path_db)
  id <- as.integer(paste0(ifelse(tipoDoc=='DNI', 1, 2), codDoc))
  
  df_clie <- DBI::dbGetQuery(
    conn = api_db, 
    statement = sprintf(
      'select Cuenta, SaldoPrincipal, DiasMora from BaseClientes where Identidad = %s', id))
  
  # Bind
  df <- dplyr::bind_cols(df, df_clie)
  
  response <- list(
    Tipo = tipoDoc,
    Documento = codDoc,
    Campaña = df$Campaña,
    Cuenta = df$Cuenta,
    Capital = format(df$SaldoPrincipal, big.mark=","),
    DiasMora = df$DiasMora,
    Vigencia = df$Vigencia
  )
  
  DBI::dbDisconnect(api_db)
  return(response)
}

# Solicitud 3: Grabar
envio_sol3 <- function(req, res) {
  jsonData <- req$postBody
  data <- fromJSON(jsonData)
  
  df <- data.frame(data)
  df$FechaSol <- as.character(Sys.Date())
  df$EstadoSol <- 'Enviada'
  df$UserSol <- user[1,2]
  df$REGISTRO <- 1
  
  path_db <- '~/1. Projects/3. RProject/PlumbeR/API_DB.db'
  api_db <- DBI::dbConnect(RSQLite::SQLite(), path_db)
  
  # Check solicitudes
  v_sol <- DBI::dbGetQuery(
    conn = api_db,
    statement = sprintf(
      "select max(FechaSol) from BaseSolicitudes
        where TIPODOC = '%s' and CODDOC = '%s' and Registro = 1",
      data$TIPODOC, data$CODDOC))[[1]]
  
  if (is.na(v_sol)) v_sol <- '2020-01-01'

  # Response
  if (as.integer(format(as.Date(v_sol),'%Y%m')) != as.integer(format(Sys.Date(),'%Y%m'))) {
    DBI::dbWriteTable(api_db, 'BaseSolicitudes', df, append = TRUE)
    response <- list(
      sprintf('Registo de solicitud exitoso para la campaña %s (%s)', data$Campaña, Sys.Date()))
  } else {
    response <- list('Error: ya existe una solicitud para el periodo en curso')
  }
  
  DBI::dbDisconnect(api_db)
  return(response)
}

# Bandeja 1: Consulta
bandeja_sol1 <- function(req, res) {
  jsonData <- req$postBody
  data <- fromJSON(jsonData)
  dni <- gsub('[^0-9]', '', data$CODDOC)
  path_db <- '~/1. Projects/3. RProject/PlumbeR/API_DB.db'
  
  if (stringr::str_length(dni)==8) {
    api_db <- DBI::dbConnect(RSQLite::SQLite(), path_db)
    tipoDoc <- data$TIPODOC
    codDoc <- data$CODDOC
    
    df_sol <- DBI::dbGetQuery(
      conn = api_db, 
      statement = sprintf(
        "select * from BaseSolicitudes where TIPODOC = '%s' and CODDOC = '%s' and REGISTRO = 1", 
        data$TIPODOC, data$CODDOC))
    
    if (nrow(df_sol) > 0) {
      df_sol <- dplyr::select(df_sol, -TIPODOC, -CODDOC, -REGISTRO)
      df_sol$nrow <- 1:nrow(df_sol)
      df_sol$Reverso <- sprintf('<a id="Reverso" href="#" onclick="AnulaSol(%i)">Anular</a>', df_sol$nrow)
      df_sol$nrow <- NULL
    } else {
      df_sol <- data.frame(Documento = data$CODDOC, Campaña = 'Cliente no cuenta con solicitudes')
    }
    
    response <- list(data1 = df_sol)
    
  } else {
    response <- list(Error = "Verificar DNI")
  }
  
  # Response
  DBI::dbDisconnect(api_db)
  return(response)
}

# Bandeja 2: Reverso
bandeja_sol2 <- function(req, res) {
  jsonData <- req$postBody
  data <- fromJSON(jsonData)

  path_db <- '~/1. Projects/3. RProject/PlumbeR/API_DB.db'
  api_db <- DBI::dbConnect(RSQLite::SQLite(), path_db)
  
  DBI::dbGetQuery(
    conn = api_db, 
    statement = sprintf(
      "update BaseSolicitudes set REGISTRO = 9 where TIPODOC = '%s' and CODDOC = '%s' and Campaña = '%s'", 
      data$TIPODOC, data$CODDOC, data$Campaña))
  
  response <- sprintf('Solicitud de campaña %s anulada para %s: %s (%s)', 
                      data$Campaña, data$TIPODOC, data$CODDOC, Sys.Date())
  
  DBI::dbDisconnect(api_db)
  return(response)
}


# APP ---------------------------------------------------------------------

# Log filter
api <- pr() %>% 
  pr_filter(
    name = 'log', 
    expr = auth, 
    serializer = serializer_html()
  )

# css
api <- api %>% 
  pr_handle(
    methods = 'GET', 
    path = '/css', 
    handler = css, 
    serializer = serializer_html(), 
  )

# js
api <- api %>% 
  pr_handle(
    methods = 'GET', 
    path = '/js', 
    handler = js, 
    serializer = serializer_html(), 
  )

# Main
api <- api %>% 
  pr_handle(
    methods = 'GET',
    path = '/PLD',
    handler = home_page, 
    serializer = serializer_html(), 
  )

# Page1
api <- api %>% 
  pr_handle(
    methods = 'GET', 
    path = '/Campanias', 
    handler = page1, 
    serializer = serializer_html()
  )

# Page2
api <- api %>% 
  pr_handle(
    methods = 'GET', 
    path = '/Bandeja', 
    handler = page2, 
    serializer = serializer_html()
  )

# Page3
api <- api %>% 
  pr_handle(
    methods = 'GET', 
    path = '/Aplicacion', 
    handler = page3, 
    serializer = serializer_html()
  )

# Welcome
api <- api %>% 
  pr_handle(
    methods = 'GET', 
    path = '/User', 
    preempt = 'log',
    handler = welcome, 
    serializer = serializer_json()
  )

# Consulta tn
api <- api %>% 
  pr_handle(
    methods = 'POST', 
    path = 'get_tn',
    preempt = 'log',
    handler = get_tn,
    serializer = serializer_json()
  )

# Validate 1
api <- api %>% 
  pr_handle(
    methods = 'POST', 
    path = 'validate1',
    preempt = 'log',
    handler = validate1,
    serializer = serializer_json()
  )

# Validate 2
api <- api %>% 
  pr_handle(
    methods = 'POST', 
    path = 'validate2',
    preempt = 'log',
    handler = validate2,
    serializer = serializer_json()
  )

# graba solicitud
api <- api %>% 
  pr_handle(
    methods = 'POST', 
    path = 'grabasol',
    preempt = 'log',
    handler = grabasol,
    serializer = serializer_json()
  )

# bandeja de solicitudes
api <- api %>% 
  pr_handle(
    methods = 'POST', 
    path = 'bandejasol',
    preempt = 'log',
    handler = bandejasol,
    serializer = serializer_json()
  )

# bandeja de solicitudes: anula
api <- api %>%
  pr_handle(
    methods = 'POST',
    path = 'anulasol',
    preempt = 'log',
    handler = anulasol,
    serializer = serializer_json()
  )

# bandeja de solicitudes: update
api <- api %>%
  pr_handle(
    methods = 'POST',
    path = 'updatesol',
    preempt = 'log',
    handler = updatesol,
    serializer = serializer_json()
  )

# upload zip file
api <- api %>%
  pr_handle(
    methods = 'POST',
    path = 'upload_file',
    preempt = 'log',
    handler = upload_file,
    serializer = serializer_content_type('multipart/form-data')
  )

# download zip file
api <- api %>%
  pr_handle(
    methods = 'GET',
    path = 'download_file',
    preempt = 'log',
    handler = download_file, 
    serializer = serializer_content_type('zip')
  )


#:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::#
#:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::#

# Consulta cob
api <- api %>% 
  pr_handle(
    methods = 'POST', 
    path = 'get_data',
    preempt = 'log',
    handler = get_data,
    serializer = serializer_json()
  )

# EnvioSol 1
api <- api %>% 
  pr_handle(
    methods = 'POST', 
    path = 'envio_sol1',
    preempt = 'log',
    handler = envio_sol1,
    serializer = serializer_json()
  )

# EnvioSol 2
api <- api %>% 
  pr_handle(
    methods = 'POST', 
    path = 'envio_sol2',
    preempt = 'log',
    handler = envio_sol2,
    serializer = serializer_json()
  )

# EnvioSol 3
api <- api %>% 
  pr_handle(
    methods = 'POST', 
    path = 'envio_sol3',
    preempt = 'log',
    handler = envio_sol3,
    serializer = serializer_json()
  )

# Bandeja 1
api <- api %>% 
  pr_handle(
    methods = 'POST', 
    path = 'bandeja_sol1',
    preempt = 'log',
    handler = bandeja_sol1,
    serializer = serializer_json()
  )

# Bandeja 2
api <- api %>% 
  pr_handle(
    methods = 'POST', 
    path = 'bandeja_sol2',
    preempt = 'log',
    handler = bandeja_sol2,
    serializer = serializer_json()
  )


# Server ------------------------------------------------------------------

# start
api$run(host = '0.0.0.0', port = 8080, swagger = F)




