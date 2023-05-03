setInterval(() => {

    const minute = 1000 * 60;
    const hour = minute * 60;
    const day = hour * 24;
    required_date = new Date('June 30, 2023 GMT+05:30');
    original_date = new Date();
    let time = required_date.getTime();
    let time2 = original_date.getTime();
    var seconds = Math.round(((time-time2)%(1000 *60)) / 1000)%60 < 10 ? '0'+Math.round(((time-time2)%(1000 *60)) / 1000)%60 : Math.round(((time-time2)%(1000 *60)) / 1000)%60;
    var minutes = Math.round(((time-time2-30000)%(hour)) / minute)%60 < 10 ? '0'+Math.round(((time-time2-30000)%(hour)) / minute)%60 : Math.round(((time-time2-30000)%(hour)) / minute)%60;
    var hours = Math.round(((time-time2-(60*30000))%(day)) / hour)%24 < 10 ? '0'+Math.round(((time-time2-(60*30000))%(day)) / hour)%24 : Math.round(((time-time2-(60*30000))%(day)) / hour)%24;
    var days = Math.round(((time-time2-(24*60*30000)) / day)) < 10 ? '0'+Math.round(((time-time2-(24*60*30000)) / day)) : Math.round(((time-time2-(24*60*30000)) / day));
    document.getElementById('secs').innerHTML = seconds;
    document.getElementById('mins').innerHTML = minutes;
    document.getElementById('hours').innerHTML = hours;
    document.getElementById('days').innerHTML = days;
}, 1000);
var displayed = "0";
window.onbeforeunload = function(event)
    {
        return confirm("Confirm refresh");
    };
function zoomin(x){
    x.style.width = "20vw";
    x.style.transition = ".4s ease-in";
    x.style.height = "20vw";
    x.style.border = "solid yellow";

}
function zoomout(x){
    x.style.width = "";
    x.style.height = "";
    x.style.border = "solid red";
}
function displayreview(){
    var todisplay = document.getElementById("toshow");
    if(displayed==="0"){
    todisplay.style.height = "max-content";
    displayed="1";
    }
    else{
        todisplay.style.height = "0px";
        displayed="0";
    }
}


    window.addEventListener("load", function(event) {
    const all_stars =document.querySelectorAll('.fa-star');
    all_stars.forEach((star, index1) => {
        star.addEventListener('click', () =>{   
            all_stars.forEach((star, index2) => {
                index1 >= index2 ? star.innerHTML = "&#9733;" : star.innerHTML = "&#9734;";
                index1 >= index2 ? star.style.color = "gold" : star.style.color = "white";
            });
        });
    });
});
  
window.addEventListener("load", function(event) {
let loginForm = document.getElementById("form_data");
list = [];  
dict = {
    "names" : [],
    "rating" : [],
    "comment" : [],
    "date" : []
}
loginForm.addEventListener("submit", (e) => {
  e.preventDefault();
  var username = window.prompt("Please provide your name: ");
  let rating = document.querySelector("input[name='rated']:checked").value;
  let comment = document.getElementById("comment-box").value;
  document.getElementById("toshow").style.height = "0px";
  displayed = "0";
    
  if (rating.value == "" || comment.value == "") {
    document.getElementById("error").innerHTML = "Sorry, You had not given a field !. Try again.";
  } else {
    document.getElementById("error").innerHTML = "Your Review has been successfully Recorded!";
    document.getElementById("comment-box").value = "";
    let stars = '';
    for (let i = 0; i < rating; i++) {
        stars += "<span>&#9733;</span>"
    }
    for (let i = rating; i < 5; i++){
        stars += "<span>&#9734;</span>"
    }
    var today = new Date();
    var month = (today.getMonth()+1) < 10 ? '0'+(today.getMonth()+1) : (today.getMonth()+1);
    var day = (today.getDate()+1) < 10 ? '0'+(today.getDate()+1) : (today.getDate()+1);
    var date = day+'/'+month+'/'+today.getFullYear();
    dict.names = username;
    dict.rating = rating;
    dict.comment = comment;
    dict.date = date;
    list.push(dict);
    localStorage.setItem("lists", list);
    document.getElementById("invisible").style.display="none";
    document.getElementById("invisibl").style.display="none";
    document.getElementById("comments").innerHTML += `
    <hr style="width: 100%;margin-top: 0.4vw;color: rgb(120, 120, 120);">
    <div class="comment-container">
    <img src="images/per.png" alt="">
    <div class="com-details">
        <div class="date">`+date+`</div>
            <h4 class="commenter-name">`+username+`</h4>
            <div class="rating-stars">Rating: `+stars+`
            </div>
            <p>"`+comment+`"</p>
        </div>    
    </div>` 
  }
  document.getElementById("error").style.display = "block";
});
});

