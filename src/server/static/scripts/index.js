$(document).ready(function() {
    index.socket = new WebSocket(index.socket_uri);
    index.socket.onmessage = function(event) {
        alert(event.data);
    };
    $("#btnScan").button().click(function() {
        var name =
            $("#txtName").val().replace(/ /g,"_").replace(/[#\.\/|&;$%@"<>()+,\\\^\[\]]/g, "");
        var source = $("#txtSource").val();
        if (name !== "") {
            var message = {
            "type":"scan",
            "name":name,
            "source":source
            };
            index.socket.send(JSON.stringify(message));
        }
    });
    });