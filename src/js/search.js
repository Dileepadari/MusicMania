window.addEventListener("load", function(event) {
    var i = 0;
    
    var txt = ' Search and Get Your favourite Artist/ Albums/ Tracks and enjoy the Samples.';
    var speed = 50;
    function typeWriter() {
    if (i < txt.length) {
        document.getElementById("message").innerHTML += txt.charAt(i);
        i++;
        setTimeout(typeWriter, speed);
    }   
    }
    typeWriter();
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
    function msToTime(s) {
        function pad(n, z) {
          z = z || 2;
          return ('00' + n).slice(-z);
        }
      
        var ms = s % 1000;
        s = (s - ms) / 1000;
        var secs = s % 60;
        s = (s - secs) / 60;
        var mins = s % 60;
        var hrs = (s - mins) / 60;
      
        return pad(hrs) + ' hrs ' + pad(mins) + ' mins ' + pad(secs) + ' secs ' + pad(ms, 3);
      }
      
      
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
                    console.log(data);
                    if(i<10){
                        i = i+1;
                    }
                    else{
                        return;
                    }
                    if((!(isNaN(maxDuration)) && data['trackTimeMillis']<=(maxDuration*1000)) || isNaN(maxDuration)){
                        if(data['trackName'] == undefined){
                            data['trackName'] = data['collectionName'];
                        }
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
                        <h4 class="time">`+msToTime(data['trackTimeMillis'])+`</h4>
                        <h4 class="time"> Explicitness : `+data['trackExplicitness']+`</h4>
                        <h4 class="num-albums">`+data['primaryGenreName']+`</h4>
                        <a href="`+data['trackViewUrl']+`" style="color: red;">More about the Track</a>
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
