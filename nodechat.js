var app = require('http');
var fs = require('fs');

app.createServer(function(req, res){
  var file = "";
  if(req.url == '/'){
    file = __dirname + '/index.html';
  } else {
    file = __dirname + req.url;
  }

  fs.readFile(file, function(err, data){
    if(err){
      res.writeHead(404);
      res.end("File not found.");
    } else {
      res.writeHead(200);
      res.end(data);
    }
  });
}).listen(3000);

console.log("app running");
