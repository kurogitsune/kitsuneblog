
//#######SETUP##########
//##Control parameters##

the_delay=40*60*10//*60*15
scroll_to_the_bottom=1 //Scroll to the bottom of the page when the page loads initially (only once)

//######################

tc=0
pc=0
pc_start=0
temp_plain=""
section_ends_after=-1
toplvl=0
buffer_html=""
preload=true

// Support TLS-specific URLs, when appropriate.
if (window.location.protocol == "https:") {
  var ws_scheme = "wss://";
} else {
  var ws_scheme = "ws://"
};

var inbox = new ReconnectingWebSocket(ws_scheme + location.host + "/receive");

inbox.onmessage = function(message) {
  
  var data = JSON.parse(message.data);

      string=data.text
      type=data.handle

      
    var dest = $('#data');
      var htmlTagRegex =/\s*(<[^>]*>)/g     

      var isTag=[]
      if (preload==true){

        if (string.indexOf("<!-- -->")>-1) {
          var postArray = string.split("<!-- -->");

          if (postArray.length>2){
            for (i=0;i<postArray.length-2;i++) {
              $("#processed").append(postArray[i])

              pc++
            }
            string=postArray[postArray.length-2]+"<!-- -->"+postArray[postArray.length-1]
          }
        }
      dest.append('<div id="post'+pc+'"></div>')
      pc++
    }
    if (toplvl==0) {
      toplvl=$("#post"+(pc-1))
    }

      tagArray = string.split(htmlTagRegex);
      for (i=0;i<tagArray.length;i++){
        if (tagArray[i].charAt(0)=="<"){
          isTag[i]=1
        } else {
          isTag[i]=0
        }

      }
      var tc_start=tc
      start_opacity=1

      for (i = 0; i <tagArray.length; i++) {
        if (section_ends_after==-1){
          temp_plain=temp_plain+tagArray[i]
        } else {
          buffer_html=buffer_html+tagArray[i]
        }
        if (isTag[i]==1){
          
          
          if (tagArray[i]=="<!-- -->"){
            section_ends_after=tc
            temp_plain=temp_plain+buffer_html
            buffer_html=""
          dest.append('<div id="post'+pc+'"></div>')
            pc++
            toplvl=$("#post"+(pc-1))


          } else {
            
          
            if (tagArray[i].charAt(1)=="/"){ //closing tag 
              if (tagArray[i]=="</h1>"){
                update_nav=1
              }
              toplvl=toplvl.parent()
            } else {
              toplvl=toplvl.append(tagArray[i])
              toplvl=$("#post"+(pc-1))
              
              while(toplvl.children().length>0){
                toplvl=toplvl.children().last()

              }
            }
          }
          
        } else {
          temp=""
          for (i1 = 0; i1 <tagArray[i].length; i1++) { 

            if (tagArray[i].substring(i1,i1+6)=="&nbsp;"){

              temp=temp+'<span id="let'+tc+'">'+"&nbsp;"+'</span>'
              tagArray[i]=tagArray[i].substring(0,i1)+tagArray[i].substring(i1+5)
          } else if (tagArray[i].substring(i1,i1+4)=="&lt;"){
              temp=temp+'<span id="let'+tc+'">'+"&lt;"+'</span>'
              tagArray[i]=tagArray[i].substring(0,i1)+tagArray[i].substring(i1+3)
            } else if (tagArray[i].substring(i1,i1+4)=="&gt;"){
              temp=temp+'<span id="let'+tc+'">'+"&gt;"+'</span>'
              tagArray[i]=tagArray[i].substring(0,i1)+tagArray[i].substring(i1+3)
            } else {
              temp=temp+'<span id="let'+tc+'">'+tagArray[i][i1]+'</span>'
            }

            tc++
          }
        
        toplvl.append(temp)
          
        }
      } 
      
      for (i=tc-1;i>=tc_start;i--){
        if (preload==true){
          if ((tc-1-i)<10){
            
            start_opacity=(tc-1-i)/10
          }
          else {
            start_opacity=1
          }
        } else {
          start_opacity=0
        }

        if ((section_ends_after>-1) && (section_ends_after==i)){
          $("#let"+i).css('opacity', start_opacity).fadeTo( 1000*2*(1-start_opacity)*the_delay , 1, function(){
            $("#processed").append(temp_plain)
            temp_plain=buffer_html
            buffer_html=""
            //clean up spans
            for(i=pc_start;i<=pc-2;i++){
              $("#post"+(i)).remove()
            }
            update_nav=1

            pc_start=pc-2
          section_ends_after=-1
          })  
        } else {
        
          $("#let"+i).css('opacity', start_opacity).fadeTo( 1000*2*(1-start_opacity)*the_delay , 1, function(){})
        }
      }
      preload=false
          if (update_nav==1){
            update_nav=0
            var temp_nav=""
            //update nav
            $("#processed").children(".post_title").each(function(index, currentElem) {
              temp_separator="&nbsp;|&nbsp;"
              if (temp_nav==""){
                temp_separator=""
              }
              temp_nav=temp_nav+temp_separator+'<A href="#'+currentElem.id+'">'+currentElem.getElementsByTagName( 'h1' )[0].childNodes[0].nodeValue+'</A>'
          });
            temp_separator="&nbsp;|&nbsp;"
          currentElem=$("#post"+(pc-1)).children(".post_title").eq(0)
          temp_nav=temp_nav+temp_separator+'<A href="#'+currentElem.attr('id')+'">'+currentElem.children("h1").eq(0).text()+'</A>'
          
          $("#nav").html(temp_nav)  
        }
};

inbox.onclose = function(){
    console.log('inbox closed');
    this.inbox = new WebSocket(inbox.url);

};