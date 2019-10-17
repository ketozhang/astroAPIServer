$("#api-button-save").click(function (e) {
    e.preventDefault()
    $("#api-form").attr('action', endpoint)
    // $(this).attr('action', window.location.origin + $("#api-form-url").val())
});
$("#api-button-inline").click(function (e) {
    e.preventDefault()
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
        error: function () {
            console.log(this.url)
        }
    })
});

$("#api-button-newtab").click(function () {
    let endpoint = window.location.origin + $("#api-form-url").val()
    $("#api-form").attr('action', endpoint)
    $(this).attr('action', window.location.origin + $("#api-form-url").val())
});