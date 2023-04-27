window.addEventListener("load", function(event) {
//     this.setInterval(()=>{
//     var i = 0;
//     document.getElementById("message").innerHTML = "";
//     var txt = ' Search and Get Your favourite Artist/ Albums/ Tracks and enjoy the Samples.';
//     var speed = 50;
//     function typeWriter() {
//     if (i < txt.length) {
//         document.getElementById("message").innerHTML += txt.charAt(i);
//         i++;
//         setTimeout(typeWriter, speed);
//     }   
//     }
//     typeWriter();
// },5000);
// });

var t_no = 0;
setInterval(()=>{
    var i = 0;
    
    document.getElementById("message").innerHTML = "";
    var txt = 'Discover the musical gems';
    var txt2 = 'Delve into the musical universe.';
    var txt3 = 'Enjoy the samples provided.';
    var speed = 50;
    function typeWriter() {
    if (i < txt.length && t_no%3 == 1) {
        document.getElementById("message").innerHTML += txt.charAt(i);
        i++;
        setTimeout(typeWriter, speed);
    }
    else if(i < txt2.length && t_no%3 == 2) {
        document.getElementById("message").innerHTML += txt2.charAt(i);
        i++;
        setTimeout(typeWriter, speed);
    }
    else if(i < txt3.length && t_no%3 == 0) {
        document.getElementById("message").innerHTML += txt3.charAt(i);
        i++;
        setTimeout(typeWriter, speed);
    }  
    }
    t_no = t_no+1;
    typeWriter();
    
},2000);
});

    var maxDuration = null;
    window.addEventListener("load", function(event) {
   document.querySelector('#search_inp').addEventListener('keypress', function (e) {
            if (e.key === 'Enter') {
              document.getElementById("search_btn").click();
            }
        });
    });
    
    var url;
    var check;
    function searchTracks() {
        i = 0;
        const search = document.getElementById('search_inp').value;
        if(isNaN(parseInt(document.getElementById('filter_check22').value))){
            maxDuration = ((parseInt(document.getElementById('filter_check21').value))*60);
        }
        else if(isNaN(parseInt(document.getElementById('filter_check21').value))){
            maxDuration = parseInt(document.getElementById('filter_check22').value);
        }
        else{
        maxDuration = ((parseInt(document.getElementById('filter_check21').value))*60)+parseInt(document.getElementById('filter_check22').value);
        }
        url = 'https://itunes.apple.com/search?term='+search+'&explicit=no&limit=10';
        document.getElementById('container').innerHTML = '';
        if(document.getElementById('filter_check1').checked){
            url = 'https://itunes.apple.com/search?term='+search+'&explicit=yes&limit=25';   
        }
        fetch(url)
            .then(response => response.json())
            .then((tracks) => {
                if (tracks.results.length === 0) {
                    document.getElementById('container').innerHTML = '<h2 class="no_res">No results found.</h2';
                    return;
                }

                tracks.results.forEach(data => {
                    if(i<10){
                        i = i+1;
                    }
                    else{
                        return;
                    }
                    if((!(isNaN(maxDuration)) && data['trackTimeMillis']<=(maxDuration*1000)) || isNaN(maxDuration)){
                    document.getElementById('container').innerHTML  += `
                    <div class="flex">
                    <div class="details">
                    <div class="block" style="display:flex;flex-direction:column;min-width:15vw;">
                        <img src="`+data['artworkUrl100']+`" alt="`+data['trackName']+`" class="artis-img">
                        <audio controls class="audio-ctrl"><source src="`+data['previewUrl']+`" type="audio/ogg"></source></audio>
                    </div>
                    <div class="det-content">
                        <h2 class="name">`+data['trackName']+`</h2>
                        <h3 class="birth">`+data['artistName']+`</h3>
                        <h4 class="languages">`+data['collectionName']+`</h4>
                        <h4 class="num-albums">`+data['primaryGenreName']+`</h4>
                        <a href="`+data['trackViewUrl']+`" style="color: yellow;">More about the Track</a>
                    </div>
                </div><br>
                    `;
                    }
                });
                if(document.getElementById('container').innerHTML == ""){
                    document.getElementById('container').innerHTML = '<h2 class="no_res">No results found.</h2';
                }
                
            })
            .catch(error => {
                console.error('Error getting tracks due to  :', error);
            });
            
    }
function clearFilters() {
    document.getElementById('filter_check1').checked = false;
    document.getElementById('filter_check21').value = '';
    document.getElementById('filter_check22').value = '';
}
