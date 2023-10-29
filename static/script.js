//Using if statements allow me to use the same script for different pages
//Avoids error: x is undefined

//universal
//Reset all inputs (they persist for some reason?)
let allcheckboxes = document.querySelectorAll("input[type='checkbox']");
//Can't umbrella-select all inputs because dropdowns/radio buttons will be broken
let alltextinputs = document.querySelectorAll("input[type='text']");
let allnuminputs = document.querySelectorAll("input[type='text']");
addEventListener("load", function() {
    for (let i of allcheckboxes) {
        i.checked = false;
    }
    for (let i of alltextinputs) {
        i.value = "";
    }
    for (let i of allnuminputs) {
        i.value = "";
    }
})

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



//workout.html
let workoutform = document.querySelector("#workoutform")

if (workoutform) {
    //Display of form
    let checkboxlist = document.querySelectorAll("input[type='checkbox']");
    let howmanychecked = 0;
    for (let mycheckbox of checkboxlist) {
        mycheckbox.addEventListener("input", function() {
            //Convert checkbox id to container div id
            //E.g. deadlift? -> deadliftdiv
            let correspondingdiv = document.querySelector(`#${mycheckbox.getAttribute("id").slice(0,-1)+"div"}`)
            
            //Add/subtract checked box counter and toggle visibility
            if (mycheckbox.checked) {
                howmanychecked += 1;
                correspondingdiv.style.visibility = "visible";
            } else {
                howmanychecked -= 1;
                correspondingdiv.style.visibility = "hidden";
            }
            //Only show text inputs if at least 1 checkbox is selected
            if (howmanychecked > 0) {
                textinputs.style.visibility = "visible";
            } else {
                textinputs.style.visibility = "hidden";
            }
        })
    }

    //Timer button functionality
    let timerbutton = document.querySelector("button#timer");
    let timespent = 0; //seconds, convert later to avoid abuse of rounding up minute
    let starttime = -1;
    let clickcounter = 0;
    let timerstopped = true;
    timerbutton.addEventListener("click", function(event) {
        //Algorithmic thinking
        event.preventDefault();
        clickcounter += 1;
        //Get current time
        let now = new Date().getTime();
        if (clickcounter % 2 == 1) {
            //Odd clicks start the timer
            starttime = now;
            timerstopped = false;
            timerbutton.textContent = "Stop timer"
        } else {
            //Even clicks end timer and add timediff to timespent
            let timediff = (now - starttime)/1000;
            timespent += timediff;
            timerstopped = true;
            console.log(timespent);
            timerbutton.textContent = "Resume timer"
        }
    })

    //Actual functionality of form
    submitworkout.addEventListener("click", async function(event) {
        event.preventDefault();
        msg.textContent = "";
        let sessionrecords = {};
        let sessionvolume = 0;

        for (let lift of ["deadlift", "squat", "bench", "overhead", "otherlift"]) {
            //String converted to list of sets (e.g. [3x80,4x90])
            let allsets = document.querySelector(`#${lift}`).value;
            allsets = allsets.split(",");
            //Store all weights lifted (e.g. [80, 90])
            let allweights = [];
            for (let set of allsets) {
                //Push only weight to array allweights
                allweights.push(set.split("x")[1]);

                //Add volume of each set to total weight lifted in session (e.g. 3x80 = 240)
                //if statement to avoid adding undefined to sessionvolume (and ending up with sessionvolume=NaN) when input is empty
                if (eval(set.replace("x", "*"))) {
                    sessionvolume += eval(set.replace("x", "*"));
                }
            }
            //Find largest item in allweights and save as session record for that lift (e.g. deadlift: 90)
            //Has to be converted to integer because it's a string, but this can be done last for efficiency because JS evaluates numeric strings as numbers
            sessionrecords[lift] = Number(allweights.reduce((max, current) => (current > max ? current : max), allweights[0]));
            
            //Avoid null values in object
            if (!sessionrecords[lift]) {
                sessionrecords[lift] = -1;
            }
        }

        //Convert timespent from seconds to minutes, bump up by 1 to include incomplete mins (e.g. 40m50s = 41m)
        timespent = Math.floor(timespent/60) + 1;

        if (!timerstopped) {
            msg.textContent = "Hey broski, stop the timer, man!"
        } else {
            let response = await window.fetch(`/workout?records=${JSON.stringify(sessionrecords)}&volume=${sessionvolume}&timespent=${timespent}`);
            response = await response.json();
            
            if (response["new records"].length > 0) {
                msg.innerHTML = "Congrats, dude, you totally, like, crushed it with new personal record(s) in: " + response["new records"] + "! <br>Radical!"
            } else {
                msg.textContent = "No new records today, bummer. Keep pushing, bro!"
            }
        }
    })
}