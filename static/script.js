//Using if statements allow me to use the same script for different pages
//Avoids error: x is undefined

//login.html
let submitlogin = document.querySelector("#submitlogin");
if (submitlogin) {
    submitlogin.addEventListener("click", async function(event) {
        //Avoid refreshing page
        event.preventDefault();
        //Take username and password from input fields, send to app.py and wait for it to respond
        let response = await window.fetch(`/login?username=${username.value.trim()}&password=${pwd.value}`);
        response = await response.json()
        if (response.type == "success") {
            msg.textContent = "Login successful";
            console.log("Login successful")
            window.location.href = "/static/homepage.html"
        } else if (response.type == "failure") {
            msg.textContent = "Login failed";
        } else {
            console.log("not working")
        }
    })
}



//register.html
let submitregister = document.querySelector("#submitregister")
if (submitregister) {
    submitregister.addEventListener("click", async function(event) {
        //Prevent reload
        event.preventDefault();
        //Make string of scheduled days by checking which input is selected
        let myschedule = ""
        for (let i of [mon, tue, wed, thu, fri, sat, sun]) {
            if (i.checked) {
                myschedule += i.name + ",";
            }
        }
        //Remove end comma from string
        myschedule = myschedule.slice(0, -1);

        //Check which style radio button (if any) is selected and set style to that
        let style;
        try {
            style = document.querySelector("input[name='style']:checked").getAttribute("id");
        } catch {
            
        }

        //Validate coordinates (2 space-separated decimals, latitude between +-90 and longitude between +-180)
        //Source https://stackoverflow.com/a/18690202 (except replaced ",\s" with single space " ")
        let coordinateregex = /^[-+]?([1-8]?\d(\.\d+)?|90(\.0+)?) *[-+]?(180(\.0+)?|((1[0-7]\d)|([1-9]?\d))(\.\d+)?)$/gm;

        //Expression validating all inputs
        const formvalid = username.value.trim().length > 0 && pwd.value.trim().length > 0 && coordinateregex.test(coords.value.trim()) && style && Number(deadlift.value) > 0 && Number(squat.value) > 0 && Number(bench.value) > 0 && Number(overhead.value) > 0 && myschedule != "";
        
        if (formvalid) {
            msg.textContent = "";
            let response = await window.fetch(`/register?username=${username.value.trim()}&pwd=${pwd.value}&coords=${coords.value.trim()}&membership=${membership.value}&style=${style}&deadlift=${deadlift.value}&squat=${squat.value}&bench=${bench.value}&&overhead=${overhead.value}&schedule=${myschedule}`);
            response = await response.json()

            if (response.usernametaken) {
                msg.textContent = "Username taken, try another"
            } else {
                msg.textContent = "Registration successful"
                window.location.href = "/static/homepage.html"
            }
        } else {
            msg.textContent = "Registration details invalid";
        }
    })
}



//homepage.html
let welcomemsg = document.querySelector("#welcomemsg");

//Needs to be async, so made a function for it
async function displayWelcomeMsg() {
    console.log("welcomemsg thingy up and running")
    let response = await window.fetch("/homepage");
    response = await response.json();
    welcomemsg.textContent = "Welcome, " + response.username;
    console.log(response.username)
}
if (welcomemsg) {
    displayWelcomeMsg();
}



//matches.html
let sortingcriterion = document.querySelector("#sortingcriterion")
if (sortingcriterion) {
    sortingcriterion.addEventListener("input", async function() {
        response = await window.fetch(`/matches?crit=${sortingcriterion.value}`);
        response = await response.json();
        //Turn list into legible format
        let matchesformatted = "";
        for (let item of response.matches) {
            matchesformatted += String(item) + "<br>";
            console.log(matchesformatted)
        }
        matchbox.innerHTML = matchesformatted;
    })
}