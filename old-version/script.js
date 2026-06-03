/* JavaScript */

/* Identifica usuario */
$(document).ready(function() {
  $.getJSON("/User", function(data) {
    var parsedData = JSON.parse(data[0]);
    var userP = document.getElementById("user");
    userP.innerHTML = "Bienvenido: " + parsedData.username;
  });
});

/* Refresh */
$(document).ready(function() {
  $("#refreshBtn").click(function() {
    location.reload();
  });
});

/* -------------------------------------------------------------------------- */
/* ------------------------------TRAMITE NORMAL------------------------------ */
/* -------------------------------------------------------------------------- */

/* Consulta clientes */
$(document).ready(function() {
  $("#submitBtn").click(function(e) {
    e.preventDefault();
    var tipoDoc = $("#tipoDoc").val();
    var codDoc = $("#codDoc").val();
    var jsonData = {
      TIPODOC: tipoDoc,
      CODDOC: codDoc
    };
    $.ajax({
      url: "/get_tn",
      type: "POST",
      contentType: "application/json",
      data: JSON.stringify(jsonData),
      success: function(response) {
        var tipoDoc = response.tipoDoc;
        var codDoc = response.codDoc;
        var estado = response.estado;
        var result = "";
        var oferta = "";
        var dataHtml1 = "<table>";
        var dataHtml2 = "<table>";
        var dataHtml3 = "<table>";
        var campHtml = "<table id='Campania'>";
        
        $.each(response, function(key, value) {
          if (key != "Error") {
            result = "Datos del Cliente:";
          };
        });
        
        $.each(response.data1, function(index, item) {
          dataHtml1 += "<table>";
          $.each(item, function(key, value) {
            dataHtml1 += "<tr>";
            dataHtml1 += "<th>" + key + "</th>";
            dataHtml1 += "<td>" + value + "</td>";
            dataHtml1 += "</tr>";
          });
          dataHtml1 += "</table>";
        });
        
        $.each(response.data2, function(index, item) {
          dataHtml2 += "<table>";
          $.each(item, function(key, value) {
            dataHtml2 += "<tr>";
            dataHtml2 += "<th>" + key + "</th>";
            dataHtml2 += "<td>" + value + "</td>";
            dataHtml2 += "</tr>";
          });
          dataHtml2 += "</table>";
        });
        
        $.each(response.data3, function(index, item) {
          dataHtml3 += "<table>";
          $.each(item, function(key, value) {
            dataHtml3 += "<tr>";
            dataHtml3 += "<th>" + key + "</th>";
            dataHtml3 += "<td>" + value + "</td>";
            dataHtml3 += "</tr>";
          });
          dataHtml3 += "</table>";
        });
        
        $.each(response, function(key, value) {
          if (key != "Error") {
            oferta = "Campañas PLD:";
          };
        });
        
        $.each(response.data4, function(index, item) {
          if (index === 0) {
            campHtml += "<tr>";
            $.each(item, function(key, value) {
              campHtml += "<th>" + key + "</th>";
            });
            campHtml += "</tr>";
          }
          campHtml += "<tr>";
          $.each(item, function(key, value) {
            campHtml += "<td>" + value + "</td>";
          });
          campHtml += "</tr>";
        });
        campHtml += "</table>";
        
        $("#output1").text(result);
        $("#output2").html(dataHtml1);
        $("#output3").html(dataHtml2);
        $("#output4").html(dataHtml3);
        $("#output5").html(oferta);
        $("#output6").html(campHtml);
      },
      error: function() {
        $("#output1").text("Error: No se pudo obtener la respuesta de la API");
      }
    });
  });
});

/* Validacion de ingresos 1 */
function Validate(Indice) {
  var tipoDoc = $("#tipoDoc").val();
  var codDoc = $("#codDoc").val();
  var table = $("#Campania")[0];
  var row = table.rows[Indice];
  var oferta = row.cells[0].innerText;
  
  var jsonData = {
    TIPODOC: tipoDoc,
    CODDOC: codDoc,
    Oferta: oferta
  };
  console.log(jsonData);
  $.ajax({
      url: "/validate1",
      type: "POST",
      contentType: "application/json",
      data: JSON.stringify(jsonData),
      success: function(response) {
        var idx = Indice;
        var solicitud = "";
        var responseHtml1 = "<table>";
        var evaluar = "";
        
        $.each(response, function(key, value) {
          if (key != "Error") {
            solicitud = "Validación de datos:";
            evaluar = "<input type='submit' value='Evaluar' id='validaIngreso' style='font-size: 20px;'>";
          };
        });
        
        $.each(response, function(key, value) {
          if (key != "Error") {
            responseHtml1 += "<tr><th>" + key + "</th><td>" + value + "</td></tr>";
          };
        });
        responseHtml1 += "</table>";
        
        $("#indice").html(idx);
        $("#resumen").html(solicitud);
        $("#resumen1").html(responseHtml1);
        $("#validaIngreso").html(evaluar);
        
      },
      error: function() {
        $("#resumen").text("Error: No se pudo obtener la respuesta de la API");
      }
    });
};

/* Validacion de ingresos 1: actualiza oferta */
$(document).ready(function() {
  $("#validaIngreso").click(function(e) {
    e.preventDefault();
    
    try {
      var tipoDoc = $("#tipoDoc").val();
      var codDoc = $("#codDoc").val();
      var idx = parseInt($("#indice").text(), 10);
      var table = $("#resumen1");
      var column = table.find("tr td:nth-child(2)");
      var cliente = column.eq(3).text().trim();
      var perfil = column.eq(4).text().trim();
      var sunedu = column.eq(5).text().trim();
      var sueldo = $("#SitLaboral").val();
      var deuda = $("#Deuda").val();
      var ingreso = $("#Ingreso").val();
      var oferta = column.eq(0).text().trim();
      var jsonData = {
        TIPODOC: tipoDoc,
        CODDOC: codDoc,
        Cliente: cliente,
        Perfil: perfil,
        Sunedu: sunedu,
        Sueldo: sueldo,
        Deuda: deuda,
        Ingreso: ingreso,
        Oferta: oferta
      };
      
      console.log(jsonData);
    } catch (error) {
      console.error('Error:', error);
    }
    
    $.ajax({
      url: "/validate2",
      type: "POST",
      contentType: "application/json",
      data: JSON.stringify(jsonData),
      success: function(response) {
        var responseHtml = "<table>";
        var respuestasol = "";
        var respuesta = "";
        var envio = "";
        var enviosol = "";
        var datasol = "";
        var alerta1 = "";
        var alerta2 = "";
        var alerta3 = "";
        
        $.each(response.data1, function(index, item) {
          responseHtml += "<table>";
          $.each(item, function(key, value) {
            responseHtml += "<tr>";
            responseHtml += "<th>" + key + "</th>";
            responseHtml += "<td>" + value + "</td>";
            responseHtml += "</tr>";
          });
          responseHtml += "</table>";
        });
        
        respuesta += "<p>" + response.respuesta[0] + "</p>";
        /*
        alerta1 += "<p style='color: red; font-weight: bold;'>" + response.alerta1[0] + "</p>";
        alerta2 += "<p style='color: red; font-weight: bold;'>" + response.alerta2[0] + "</p>";
        alerta3 += "<p style='color: red; font-weight: bold;'>" + response.alerta3[0] + "</p>";
        */
        $.each(response, function(key, value) {
          if (key != "Error") {
            envio = "Envío de Solicitud:";
            enviosol = "<input type='submit' value='Enviar' id='EnvioSol' style='font-size: 20px;'>";
          };
        });
        
        $.each(response.data2, function(index, item) {
          datasol += "<table>";
          $.each(item, function(key, value) {
            datasol += "<tr>";
            datasol += "<th>" + key + "</th>";
            datasol += "<td>" + value + "</td>";
            datasol += "</tr>";
          });
          datasol += "</table>";
        });
        
        $("#Resultado").html(responseHtml);
        $("#Respuesta").html(respuesta);
        $("#Envio").html(envio);
        $("#DataSol").html(datasol);
        $("#EnvioSol").html(enviosol);
        $("#Alerta1").html(alerta1);
        $("#Alerta2").html(alerta2);
        $("#Alerta3").html(alerta3);
        $("#RespuestaSol").html(respuestasol);

      },
      error: function() {
        $("#Resultado").text("Error: No se pudo obtener la respuesta de la API");
      }
    }); 
  });
});

/* Consulta: Envia Solicitud */
$(document).ready(function() {
  $("#EnvioSol").click(function(e) {
    e.preventDefault();
    
    var tipoDoc = $("#tipoDoc").val();
    var codDoc = $("#codDoc").val();
    var table = $("#DataSol");
    var column = table.find("tr td:nth-child(2)");
    var campania = column.eq(2).text().trim();
    var monto = $("#Solicitado").val();
    var comment = $("#Comentario").val();
    var resumen = $("#resumen1");
    var column2 = resumen.find("tr td:nth-child(2)");
    var cliente = column2.eq(3).text().trim();
    var perfil = column2.eq(4).text().trim();
    var evaluacion = $("#Resultado");
    var column3 = evaluacion.find("tr td:nth-child(2)");
    var segmento = column3.eq(0).text().trim();
    var sueldo = $("#SitLaboral").val();
    var ingreso = column3.eq(1).text().trim();
    var rci = column3.eq(2).text().trim();
    var oferta = column3.eq(3).text().trim();
    var cuota = column3.eq(4).text().trim();
    var tasa = column3.eq(5).text().trim();
    var plazo = column3.eq(6).text().trim();
    
    var jsonData = {
      TIPODOC: tipoDoc,
      CODDOC: codDoc,
      Campania: campania,
      Monto: monto,
      Comentario: comment,
      Cliente: cliente,
      Perfil: perfil,
      Segmento: segmento,
      Sueldo: sueldo,
      Ingreso: ingreso,
      RCI: rci,
      Oferta: oferta,
      Cuota: cuota,
      Plazo: plazo,
      Tasa: tasa
    };
    
    console.log(jsonData);
    
    $.ajax({
      url: "/grabasol",
      type: "POST",
      contentType: "application/json",
      data: JSON.stringify(jsonData),
      success: function(response) {
        var respuesta = "<p ";
        
        if (response.respuesta[0].toLowerCase().includes("error")) {
          respuesta += "style='color: red; font-weight: bold;'>";
          respuesta += response.respuesta[0];
        } else {
          respuesta += "style='color: navy; font-weight: bold;'>";
          respuesta += response.respuesta[0];
        };
        respuesta += "</p>";
        
        $("#RespuestaSol").html(respuesta);
      },
      error: function() {
        $("#RespuestaSol").text("Error: No se pudo obtener la respuesta de la API");
      }
    });
  });
});

/* Consulta: Bandeja de solicitudes */
$(document).ready(function() {
  $("#submitBanTN").click(function(e) {
    e.preventDefault();
    var periodo = $("#periodo").val();
    var jsonData = {
      Periodo: periodo
    };
    $.ajax({
      url: "/bandejasol",
      type: "POST",
      contentType: "application/json",
      data: JSON.stringify(jsonData),
      success: function(response) {
        var bandeja = "";
        var descarga = "";
        var bandejaHtml = "<table id='DetalleBandeja' style='width: 100%;'>";
        
        $.each(response, function(key, value) {
          if (key != "Error") {
            bandeja = "Solicitudes Enviadas:";
            descarga = "<input type='submit' value='Descarga' id='DescargaBtn' onclick='descargarCSV()'>";
          };
        });
        
        $.each(response.data1, function(index, item) {
          if (index === 0) {
            bandejaHtml += "<tr>";
            $.each(item, function(key, value) {
              bandejaHtml += "<th style='font-size: 14px;'>" + key + "</th>";
            });
            bandejaHtml += "</tr>";
          }
          bandejaHtml += "<tr>";
          $.each(item, function(key, value) {
            bandejaHtml += "<td style='font-size: 12px;'>" + value + "</td>";
          });
          bandejaHtml += "</tr>";
        });
        bandejaHtml += "</table>";
        
        $("#Bandeja").html(bandeja);
        $("#DescargaBtn").html(descarga);
        $("#Detalle").html(bandejaHtml);
      },
      error: function() {
        $("#output5").text("Error: No se pudo obtener la respuesta de la API");
      }
    });
  });
});

/* Bandeja de solicitudes: Anulacion */
function AnulaSolTN(Indice) {
  var table = $("#DetalleBandeja")[0];
  var row = table.rows[Indice];
  var codDoc = row.cells[2].innerText;
  var campaña = row.cells[3].innerText;
  var fechasol = row.cells[14].innerText;
  var periodo = $("#periodo").val();
  
  var jsonData = {
    Periodo: periodo,
    FechaSol: fechasol,
    CODDOC: codDoc,
    Campaña: campaña
  };
  console.log(jsonData);
  
  $.ajax({
      url: "/anulasol",
      type: "POST",
      contentType: "application/json",
      data: JSON.stringify(jsonData),
      success: function(response) {
        var reverso = '';
        var resultado = "<p>";
        var selector = "#Reverso" + Indice;
        
        $.each(response, function(key, value) {
          resultado += value + "</p>";
          reverso += 'Anulada';
        });
        
        $("#Resultado").html(resultado);
        $(selector).html(reverso);
        $(selector).removeAttr("href");
        $(selector).removeAttr("onclick");
        
      },
      error: function() {
        $("#resumen").text("Error: No se pudo obtener la respuesta de la API");
      }
    });
};

/* Bandeja de solicitudes: Aprobacion */
function ShowUpdateSolTN(Indice) {
  var selector = "#UpdateSol" + Indice;
  $(selector).toggle();
};

function UpdateSolTN(Indice) {
  var table = $("#DetalleBandeja")[0];
  var row = table.rows[Indice];
  var codDoc = row.cells[2].innerText;
  var campaña = row.cells[3].innerText;
  var fechasol = row.cells[14].innerText;
  var periodo = $("#periodo").val();
  var selector = "#EstadoUP" + Indice;
  var estado = $(selector).val();
  
  var jsonData = {
    Periodo: periodo,
    FechaSol: fechasol,
    CODDOC: codDoc,
    Campaña: campaña,
    EstdoUP: estado
  };
  console.log(jsonData);
  
  $.ajax({
      url: "/updatesol",
      type: "POST",
      contentType: "application/json",
      data: JSON.stringify(jsonData),
      success: function(response) {
        var resultado = "";
        var selector = "#ResEstadoUP" + Indice;
        
        $.each(response, function(key, value) {
          resultado += value + "</p>";
        });
        
        $(selector).html(resultado);
      },
      error: function() {
        $("#resumen").text("Error: No se pudo obtener la respuesta de la API");
      }
    });
    
  ShowUpdateSolTN(Indice);
  $("#submitBanTN").click();
};

/* Descarga */
function descargarCSV() {
  var tabla = document.getElementById("DetalleBandeja");
  var csv = [];
  var filas = tabla.querySelectorAll("tr");
  
  for (var i = 0; i < filas.length; i++) {
    var fila = filas[i];
    var rowData = [];
    var celdas = fila.querySelectorAll("th, td");
    for (var j = 0; j < celdas.length; j++) {
      rowData.push(celdas[j].innerText);
    }
    csv.push(rowData.join("|"));
  };
  
  var csvContent = csv.join("\n");
  var blob = new Blob([csvContent], { type: "text/csv;charset=utf-8" });
  
  var link = document.createElement("a");
  link.setAttribute("href", URL.createObjectURL(blob));
  link.setAttribute("download", "BandejaTN.csv");
  link.style.display = "none";
  
  document.body.appendChild(link);
  link.click();
  
  document.body.removeChild(link);
  
};

/* Upload file */
$(document).ready(function() {
  $("#uploadFile").click(function(e) {
    e.preventDefault();
    
    var file = $('#fileInput')[0].files[0];
    var formData = new FormData();
    var maxSizeMB = 10;
    
    formData.append('req', file);
    
    if (!file) {
      alert('Debe seleccionar un archivo.');
      $("#refreshBtn").click();
      return;
    };
    
    if (file.type !== 'application/x-zip-compressed') {
      alert('El archivo debe tener extensión .zip para ser aceptado.');
      $("#refreshBtn").click();
      return;
    };
    
    if (file.size > maxSizeMB * 1024 * 1024) {
      alert('Tamaño máximo permitido del archivoñ es de 10 MB.');
      $("#refreshBtn").click();
      return;
    };
    
    $.ajax({
      url: "/upload_file",
      type: "POST",
      data: formData,
      contentType: false,
      processData: false,
      success: function(res) {
        var result = res;
        $("#output1").html(result);
      },
      error: function() {
        console.log('Error!');
      }
    });
  });
});

/* Download file */
$(document).ready(function() {
  $("#downloadFile").click(function(e) {
    e.preventDefault();
    
    var fileName = "Senior.zip";
    var urlDownload = "/download_file?filename=" + fileName;
    var tmpLink = document.createElement('a');
    
    tmpLink.href = urlDownload;
    tmpLink.setAttribute('download', fileName);
    tmpLink.click();
    
  });
});


/* -------------------------------------------------------------------------- */
/* --------------------------CAMPAÑAS DE COBRANZAS--------------------------- */
/* -------------------------------------------------------------------------- */

/* Consulta */
$(document).ready(function() {
  $("#submitSol").click(function(e) {
    e.preventDefault();
    var tipoDoc = $("#tipoDoc").val();
    var codDoc = $("#codDoc").val();
    var jsonData = {
      TIPODOC: tipoDoc,
      CODDOC: codDoc
    };
    $.ajax({
      url: "/get_data",
      type: "POST",
      contentType: "application/json",
      data: JSON.stringify(jsonData),
      success: function(response) {
        var result = "Datos del Cliente:";
        var responseHtml = "<table>";
        var dataHtml1 = "<table>";
        var dataHtml2 = "<table>";
        
        $.each(response, function(key, value) {
          if (key != "data1" && key != "data2" && key != "data3") {
            responseHtml += "<tr><th>" + key + "</th><td>" + value + "</td></tr>";
          };
        });
        responseHtml += "</table>";
        
        $.each(response.data1, function(index, item) {
          dataHtml1 += "<table>";
          $.each(item, function(key, value) {
            dataHtml1 += "<tr>";
            dataHtml1 += "<th>" + key + "</th>";
            dataHtml1 += "<td>" + value + "</td>";
            dataHtml1 += "</tr>";
          });
          dataHtml1 += "</table>";
        });
        
        $.each(response.data2, function(index, item) {
          dataHtml2 += "<table>";
          $.each(item, function(key, value) {
            dataHtml2 += "<tr>";
            dataHtml2 += "<th>" + key + "</th>";
            dataHtml2 += "<td>" + value + "</td>";
            dataHtml2 += "</tr>";
          });
          dataHtml2 += "</table>";
        });
        
        $("#output1").text(result);
        $("#output2").html(responseHtml);
        $("#output3").html(dataHtml1);
        $("#output4").html(dataHtml2);
      },
      error: function() {
        $("#output5").text("Error: No se pudo obtener la respuesta de la API");
      }
    });
    
    $.ajax({
      url: "/envio_sol1",
      type: "POST",
      contentType: "application/json",
      data: JSON.stringify(jsonData),
      success: function(response) {
        var oferta = "";
        var campHtml = "<table id='Campania'>";
        
        $.each(response, function(key, value) {
          if (key != "Error") {
            oferta = "Campañas de Cobranza:";
          };
        });
        
        $.each(response.data1, function(index, item) {
          if (index === 0) {
            campHtml += "<tr>";
            $.each(item, function(key, value) {
              campHtml += "<th>" + key + "</th>";
            });
            campHtml += "</tr>";
          }
          campHtml += "<tr>";
          $.each(item, function(key, value) {
            campHtml += "<td>" + value + "</td>";
          });
          campHtml += "</tr>";
        });
        campHtml += "</table>";
        
        $("#output5").html(oferta);
        $("#output6").html(campHtml);
      },
      error: function() {
        $("#output5").text("Error: No se pudo obtener la respuesta de la API");
      }
    });
  });
});

/* Envio de solicitudes: Resumen */
function EnviaSol(Indice) {
  var tipoDoc = $("#tipoDoc").val();
  var codDoc = $("#codDoc").val();
  var table = $("#Campania")[0];
  var row = table.rows[Indice];
  var campaña = row.cells[0].innerText;
  var vigencia = row.cells[6].innerText;
  
  var jsonData = {
    TIPODOC: tipoDoc,
    CODDOC: codDoc,
    Campaña: campaña,
    Vigencia: vigencia
  };
  console.log(jsonData);
  $.ajax({
      url: "/envio_sol2",
      type: "POST",
      contentType: "application/json",
      data: JSON.stringify(jsonData),
      success: function(response) {
        var idx = Indice;
        var solicitud = "";
        var responseHtml1 = "<table>";
        var responseHtml2 = "<table>";
        var grabar = "";
        var resultado = "";
        
        $.each(response, function(key, value) {
          if (key != "Error") {
            solicitud = "Resumen de Solicitud:";
            grabar = "<input type='submit' value='Grabar' id='grabarSol'>";
          };
        });
        
        $.each(response, function(key, value) {
          if (key != "Condicion") {
            responseHtml1 += "<tr><th>" + key + "</th><td>" + value + "</td></tr>";
          };
        });
        responseHtml1 += "</table>";
        
        $("#indice").html(idx);
        $("#resumen").html(solicitud);
        $("#resumen1").html(responseHtml1);
        $("#resumen2").html(responseHtml2);
        $("#grabar").html(grabar);
        $("#Resultado").html(resultado);
        
      },
      error: function() {
        $("#resumen").text("Error: No se pudo obtener la respuesta de la API");
      }
    });
};

/* Graba Solicitud */
$(document).ready(function() {
  $("#grabar").click(function(e) {
    e.preventDefault();
    
    try {
      var tipoDoc = $("#tipoDoc").val();
      var codDoc = $("#codDoc").val();
      var idx = parseInt($("#indice").text(), 10);
      var table = $("#Campania")[0];
      var row = table.rows[idx];
      var campaña = row.cells[0].innerText;
      var gracia = row.cells[1].innerText;
      var dcapital = row.cells[2].innerText;
      var dinteres = row.cells[3].innerText;
      var dmora = row.cells[4].innerText;
      var dicv = row.cells[5].innerText;
      var vigencia = row.cells[6].innerText;
      
      var jsonData = {
        TIPODOC: tipoDoc,
        CODDOC: codDoc,
        Campaña: campaña,
        PeriodoGracia: gracia,
        DctoCapital: dcapital,
        Dctointeres: dinteres,
        DctoMora: dmora,
        DctoICV: dicv,
        Vigencia: vigencia
      };
      
      console.log(jsonData);
    } catch (error) {
      console.error('Error:', error);
    }
    
    $.ajax({
      url: "/envio_sol3",
      type: "POST",
      contentType: "application/json",
      data: JSON.stringify(jsonData),
      success: function(response) {
        var etiqueta = "<p ";
        var responseHtml = "";
        
        $.each(response, function(key, value) {
          responseHtml += value + "</p>";
        });
        
        if (responseHtml.toLowerCase().includes("error")) {
          etiqueta += "style='color: red; font-weight: bold;'>";
        } else {
          etiqueta += "style='color: navy;'>";
        };
        
        responseHtml = etiqueta + responseHtml;
        $("#Resultado").html(responseHtml);

      },
      error: function() {
        $("#Resultado").text("Error: No se pudo obtener la respuesta de la API");
      }
    });
  });
});

/* Bandeja de solicitudes: Consulta */
$(document).ready(function() {
  $("#submitBan").click(function(e) {
    e.preventDefault();
    var tipoDoc = $("#tipoDoc").val();
    var codDoc = $("#codDoc").val();
    var jsonData = {
      TIPODOC: tipoDoc,
      CODDOC: codDoc
    };
    $.ajax({
      url: "/bandeja_sol1",
      type: "POST",
      contentType: "application/json",
      data: JSON.stringify(jsonData),
      success: function(response) {
        var solicitud = "";
        var campHtml = "<table id='Campania'>";
        
        $.each(response, function(key, value) {
          if (key != "Error") {
            solicitud = "Campañas de Cobranza:";
          };
        });
        
        $.each(response.data1, function(index, item) {
          if (index === 0) {
            campHtml += "<tr>";
            $.each(item, function(key, value) {
              campHtml += "<th>" + key + "</th>";
            });
            campHtml += "</tr>";
          }
          campHtml += "<tr>";
          $.each(item, function(key, value) {
            campHtml += "<td>" + value + "</td>";
          });
          campHtml += "</tr>";
        });
        campHtml += "</table>";
        
        $("#output5").html(solicitud);
        $("#output6").html(campHtml);
      },
      error: function() {
        $("#output5").text("Error: No se pudo obtener la respuesta de la API");
      }
    });
  });
});

/* Bandeja de solicitudes: Anulacion */
function AnulaSol(Indice) {
  var tipoDoc = $("#tipoDoc").val();
  var codDoc = $("#codDoc").val();
  var table = $("#Campania")[0];
  var row = table.rows[Indice];
  var campaña = row.cells[0].innerText;
  var vigencia = row.cells[6].innerText;
  
  var jsonData = {
    TIPODOC: tipoDoc,
    CODDOC: codDoc,
    Campaña: campaña,
    Vigencia: vigencia
  };
  console.log(jsonData);
  $.ajax({
      url: "/bandeja_sol2",
      type: "POST",
      contentType: "application/json",
      data: JSON.stringify(jsonData),
      success: function(response) {
        var reverso = '';
        var resultado = "<p>";
        
        $.each(response, function(key, value) {
          resultado += value + "</p>";
          reverso += 'Anulada';
        });
        
        $("#Resultado").html(resultado);
        $("#Reverso").html(reverso);
        $("#Reverso").removeAttr("href");
        $("#Reverso").removeAttr("onclick");
        
      },
      error: function() {
        $("#resumen").text("Error: No se pudo obtener la respuesta de la API");
      }
    });
};
