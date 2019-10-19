$("#api-form").submit(function (e) {
    e.preventDefault();
    let printMethod = $('#print-method').val();
    if (printMethod == 'inline') { printInline(); }
    else if (printMethod == 'newtab') { printNewTab(); }
    else if (printMethod == 'newtab') { printToFile(); }
    else { return false; }
});

function printToFile() {
    e.preventDefault()
    $("#api-form").attr('action', endpoint)
    // $(this).attr('action', window.location.origin + $("#api-form-url").val())
};

function printInline() {
    $("#result-code").html("...")
    url = $("#api-form-url").val()
    if (url == '') {
        url = $("#api-form-url").attr("placeholder")
    }
    let endpoint = window.location.origin + url
    $.ajax({
        type: "get",
        url: endpoint,
        data: $("#api-form").serialize(),
        success: function (output) {
            console.log(this.url)
            if (typeof output === 'object') {
                $("#result-code").html(JSON.stringify(output, null, 2))
            } else {
                $("#result-code").html(output)
            }
        },
        error: function (jqXHR, textStatus, errorThrown) {
            console.log(this.url)
            $("#result-code").html(`<p class="text-danger">${textStatus}<br>${errorThrown}</p>`)
        }
    })
};

function printNewTab() {
    let formArgs = "newtab=true" + "&" + $("#api-form").serialize();
    let url = $("#api-form-url").val();
    if (url == "") {
        url = $("#api-form-url").attr('placeholder');
    }

    let urlArgs;
    [url, urlArgs] = url.split("?");

    if (urlArgs !== "undefined") {
        formArgs += '&' + urlArgs;
    }

    let endpoint = window.location.origin + url + '?' + formArgs;

    window.open(endpoint)
}