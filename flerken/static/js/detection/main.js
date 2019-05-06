$().ready(function(){

    $(".nav-on").click(function(){
        $("header .pull-right").slideToggle();
    });

    //clear command text area
    $('.clear').click(function(){
        $('.note-editable').html('')
    });

    $(".note-editable").on("paste", function (e) {
        textInit(e)
    });
     
    function textInit(e) {
        e.preventDefault();
        var text;
        var clp = (e.originalEvent || e).clipboardData;
        if (clp === undefined || clp === null) {
            text = window.clipboardData.getData("text") || "";
            if (text !== "") {
                if (window.getSelection) {
                    var newNode = document.createElement("span");
                    newNode.innerHTML = text;
                    window.getSelection().getRangeAt(0).insertNode(newNode);
                } else {
                    document.selection.createRange().pasteHTML(text);
                }
            }
        } else {
            text = clp.getData('text/plain') || "";
            if (text !== "") {
                document.execCommand('insertText', false, text);
            }
        }
    }

    function parseEditorContent(source){
        content_list = []
        if ((source[0].children).length == 0){
            content = source.text();
            //console.log(content);
            content = content.replace(/(^\s*)|(\s*$)/g,"");
            content = content.replace(/\s/g,'&nbsp;');
            //console.log(content);
            return content;
        }
        else{
            for (var i = 0;i<(source[0].children).length;i++){
                if (source[0].children[i].innerHTML != '<br>'){ 
                    content_list.push((source[0].children[i].innerHTML).replace(/(^\s*)|(\s*$)/g,"").replace(/\s/g,'&nbsp;'));
                }
            }
            //console.log(content_list);
            content = content_list.join("");
            first_content = (source[0].innerHTML.split('\n')[0].split('<')[0]).replace(/(^\s*)|(\s*$)/g,"").replace(/\s/g,'&nbsp;');
            content =  first_content + content;
            //console.log(content);
            return content;
        }
    }

    //move the detection area smoothly
    function moveUp(area,unit,px){
        for (var x = Math.floor(px/unit);x>0;x--){
            area.css('margin-top',(x*unit).toString()+'px');
        }
        area.css('margin-top',(px-(Math.floor(px/unit)*unit)).toString()+'px');
        area.css('margin-top','0px');
    }

    //send command to server side
    $('.detect').click(function(){
        var csrf_token = $('meta[name=X-CSRFToken]').attr('content');
        var data = {};
        data.cmd = $.trim(parseEditorContent($('.note-editable')));
        data.platform = $('select').val();
        //console.log(data.cmd.length);
        if (data.cmd.length != 0){
            $('h1').slideUp(100);
            moveUp($('.detection'),10, 110);
            $('.loading').css('display','block');
        }
        $.ajaxSetup({
            beforeSend: function(xhr, settings) {
                if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
                    xhr.setRequestHeader("X-CSRFToken", csrf_token);
                }
            }
        });
        setTimeout(function(){
        $.ajax({
            url: "/v1/detect/result.json",
            method: "POST",
            data: data,
            dataType: 'json',
            success: function(succ){
                console.log(succ);
                if (succ['res'] == 0){
                    $('.loading').slideUp();
                    $('.result').fadeIn();
                    $('.hash').text(succ['hash']);
                    if (succ['cmd'].length > 500){
                        $('.cmd').text(succ['cmd'].slice(0,500)+ "...");
                    }
                    else{
                        $('.cmd').text(succ['cmd']);
                    }
                    $('.obfuscated').text(succ['obfuscated']);
                    $('.obfuscated').css('color','#f47233');
                    $('.obfuscated').css('font-weight','800');
                    $('.reason').text(succ['reason']);
                    $('.reason').css('color','#f47233');
                    $('.reason').css('font-weight','800');
                    $('.measure_time').text(succ['measure_time']);
                    if (succ.hasOwnProperty('likely_platform')){
                        $('td').eq(4).html('<strong>Likely Platform</strong>')
                        $('.likely_platform').text(succ['likely_platform']);
                        $('.likely_platform').css('color','#f47233');
                        $('.likely_platform').css('font-weight','800');
                    }
                    else{
                        $('td').eq(4).html('<strong>Platform</strong>');
                        $('.likely_platform').text(succ['platform']);
                        $('.likely_platform').css('color','#f47233');
                        $('.likely_platform').css('font-weight','800');
                    }
                }
                else{
                    $.notify({
                        icon: 'fa fa-bell',
                        message: succ['message']
                    });
                }
            },
            error: function(err){
                console.log(err);
            }
        })},600);
        
    });
});