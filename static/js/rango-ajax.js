

$('#likes').click(function(){
    var catid;
    console.log("pishki");
    catid = $(this).attr("data-catid");
    $.get('/rango/like_category/', {category_id: catid}, function(data){
        $('#like_count').html(data);
        $('#likes').hide();
    });
});


$('#suggestion').keyup(function(){
    var query;
    query = $(this).val();

    $.get('/rango/suggest_category/', {suggestion: query}, function(data){
        var print_vals;
        for(var i = 0; i < data.length; i++){
            console.log(data[i].url);
            print_vals = "<a href=\" " + data[i].url + " \">" + data[i].name + " </a>" + "</br>";
        }
        $('#cats').html(data);
    });
});
