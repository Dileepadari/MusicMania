function add_to_play(song_id){
let data = {
    id: song_id
}
if(document.getElementById(song_id).innerHTML == "add"){
fetch('/add_to_playlist', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify(data)
})
.then(response => response.json())
.then(data => {
    console.log(data);
    document.getElementById(song_id).innerHTML = "Remove";
    document.getElementById("msg").innerHTML = "Added to Playlist";
    setTimeout(function(){
        document.getElementById("msg").innerHTML="";
        },3000);
})
.catch(error => {
    console.error(error);
});

}
else{
    fetch('/remove_from_playlist', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        console.log(data);
        document.getElementById(song_id).innerHTML = "add";
        document.getElementById("msg").innerHTML = "Removed from Playlist";
        setTimeout(function(){
            document.getElementById("msg").innerHTML="";
            },3000);
    })
    .catch(error => {
        console.error(error);
    });
    
}
}

function remove_from_playlist(song_id){
        let data = {
            id: song_id
        }
            fetch('/remove_from_playlist', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            })
            .then(response => response.json())
            .then(data => {
                console.log(data);
                document.getElementById(song_id).innerHTML = "";
                document.getElementById("msg").innerHTML = "Removed from Playlist";
                setTimeout(function(){
                    document.getElementById("msg").innerHTML="";
                    },3000);
            })
            .catch(error => {
                console.error(error);
            });
        
}