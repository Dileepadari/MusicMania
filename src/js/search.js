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
    function searchTracks() {
        i = 0;
        const search = document.getElementById('search_inp').value;
        maxDuration = ((parseInt(document.getElementById('filter_check21').value))*60)+parseInt(document.getElementById('filter_check22').value);
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
                    <div>
                    <div class="details">
                    <div class="block" style="display:flex;flex-direction:column;">
                        <img src="`+data['artworkUrl100']+`" alt="`+data['trackName']+`" class="artist-img">
                        <audio controls class="audio-ctrl"><source src="`+data['previewUrl']+`" type="audio/ogg"></source></audio>
                    </div>
                    <div class="det-content">
                        <h2 class="name">`+data['trackName']+`</h2>
                        <h3 class="birth">`+data['artistName']+`</h3>
                        <h4 class="languages">`+data['collectionName']+`</h4>
                        <h4 class="num-albums">`+data['primaryGenreName']+`</h4>
                        <a href="`+data['trackViewUrl']+`" style="color: red;">More about the Track</a>
                    </div>
                </div><br>
                    `;
                    }
                });
                
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
