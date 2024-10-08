//Using if statements allow me to use the same script for different pages
//Avoids error: x is undefined

//universal
//Reset all inputs (they persist for some reason?)
let allcheckboxes = document.querySelectorAll("input[type='checkbox']");
//Can't umbrella-select all inputs because dropdowns/radio buttons will be broken
let alltextinputs = document.querySelectorAll("input[type='text']");
let allnuminputs = document.querySelectorAll("input[type='number']");
addEventListener("load", function() {
    for (let i of allcheckboxes) {
        i.checked = false;
    }
    for (let i of alltextinputs) {
        i.value = "";
    }
    for (let i of allnuminputs) {
        i.value = 0;
    }
})
//Dark mode is tthe default style, so no if statement needed for it
if (localStorage.getItem("displaymode") == "light") {
    document.body.classList.add("light-mode"); //Light mode class has different colours
}
//Toggle light/dark mode
togglelightmode.addEventListener("click", function() {
    document.body.classList.toggle("light-mode"); //Add/remove light-mode from class list
    //Toggle saved colour mode - change to opposite of current mode
    if (localStorage.getItem("displaymode") == "dark") {
        localStorage.setItem("displaymode", "light")
    } else {
        localStorage.setItem("displaymode", "dark")
    }
})

//all pages once logged in
let dropdownbtn = document.querySelector("#dropdownbtn");
//Show username in dropdown menu in navbar
//Needs to be async, so made a function for it
async function displayusernameindropdown() {
    let response = await window.fetch("/username");
    response = await response.json();
    if (response.username != false) {
        dropdownbtn.textContent = response.username + " ⏷";
    } else {
        //If server doesn't return a username, the user has logged out
        window.location.href = "/static/login.html";
    }
}
let notifsicon = document.querySelector("#gonotifs>img")
async function shownewnotifs() {
    let response = await window.fetch("/getfriendreqs");
    response = await response.json();

    if (response.data.length > 0) {
        notifsicon.src = "/static/resources/bellactive.png";
    } else {
        notifsicon.src = "/static/resources/bell.png";
    }
}
if (dropdownbtn) {
    displayusernameindropdown();
    shownewnotifs();
    logout.addEventListener("click", async function() {
        //Delete current username
        let response = await window.fetch("/logout");
        window.location.href="/static/login.html";
    })
    logo.addEventListener("click", function() {
        window.location.href = "/static/homepage.html";
    })
    gonotifs.addEventListener("click", function() {
        window.location.href = "/static/notifications.html";
    })
}

//Password encryption - sha256 hash
//Other details (username, lift totals etc.) don't need to be encrypted
    //Because they're public (in leaderboards/friends) anyway
    async function hash(mypwd) {
        //Encode mypwd to UTF-8 standard
        const utf8 = new TextEncoder().encode(mypwd);
        //Create sha256 hash out of the encoded input
            //This is an ArrayBuffer object, so unwieldy to store
        const hash_buffer = await crypto.subtle.digest('SHA-256', utf8);
    
    //Convert sha256 hash to hex form to make it more readable and simpler to store
        //First convert the hash to an array of bytes
        const hash_array = Array.from(new Uint8Array(hash_buffer));
        //Then convert the array to a hex string
        const hash_hex = hash_array
          .map((byte) => byte.toString(16) //Convert each byte in the array to hex form
          .padStart(2, '0')) //Add leading 0s if necessary (e.g. "0a" instead of a) for consistent format
          .join(''); //Convert the array of formatted bytes to a string
    
        //Return the hex form of the sha256 hash
        return hash_hex;
    }

//login.html
let submitlogin = document.querySelector("#submitlogin");
/*
This one script.js file is run on every page to avoid file clutter
But only login.html has element #submitlogin
Trying to manipulate #submitlogin on any page other than login.html will throw a ReferenceError
because we are trying to change an element that is undefined there
So query selector and if-statement used so #submitlogin is only manipulated on the right page
*/
if (submitlogin) {
    submitlogin.addEventListener("click", async function(event) {
        //Avoid refreshing page
        event.preventDefault();
        //Encrypt password
        let pwd_encrypted = await hash(pwd.value);
        //Take username and password from input fields, send to app.py and wait for it to respond
        let response = await window.fetch(`/login?username=${username.value.trim()}&password=${pwd_encrypted}`);
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


function whichselected(sourcelist) {
    let selected = "";
    for (let i of sourcelist) {
        if (i.checked) {
            selected += i.name + ",";
        }
    }
    return selected.slice(0, -1)
}
//register.html
let submitregister = document.querySelector("#submitregister")
if (submitregister) {
    submitregister.addEventListener("click", async function(event) {
        //Prevent reload
        event.preventDefault();
        //Make string of scheduled days by checking which input is selected
        let myschedule = whichselected([mon, tue, wed, thu, fri, sat, sun]);

        //Check which style radio button (if any) is selected and set style to that
        let style;
        try {
            style = document.querySelector("input[name='style']:checked").getAttribute("id");
        } catch {
            
        }

        //borysa 15, warsaw, poland
        const numberafterstreet  = /^[^,]+ \d+, [^,]+, [^,]+$/;
        //23 elm street, portland, usa
        const streetafternumber = /^\d+ [^,]+, [^,]+, [^,]+$/;

        //Expression validating all inputs
        const formvalid = username.value.trim().length > 0 && pwd.value.trim().length > 0 && (numberafterstreet.test(address.value) || streetafternumber.test(address.value)) && style && Number(deadlift.value) > 0 && Number(squat.value) > 0 && Number(bench.value) > 0 && Number(overhead.value) > 0 && myschedule != "";
        let pwd_encrypted = await hash(pwd.value);
        if (formvalid) {
            msg.textContent = "";
            let response = await window.fetch(`/register?username=${username.value.trim()}&pwd=${pwd_encrypted}&address=${address.value.trim()}&membership=${membership.value}&style=${style}&deadlift=${deadlift.value}&squat=${squat.value}&bench=${bench.value}&&overhead=${overhead.value}&schedule=${myschedule}`);
            response = await response.json()

            if (response.error) {
                if (response.errortype == "usernametaken") {
                    msg.textContent = "Username taken, try again."
                } else if (response.errortype == "invalidaddress") {
                    msg.textContent = "Invalid address, try again."
                }
            } else {
                msg.textContent = "Registration successful"
                window.location.href = "/static/homepage.html"
            }
        } else {
            msg.textContent = "Registration details invalid, try again.";
        }
    })
}



//homepage.html
let welcomemsg = document.querySelector("#welcomemsg");

//Needs to be async, so made a function for it
async function displaywelcome() {
    let response = await window.fetch("/username");
    response = await response.json();
    //Welcome message
    welcomemsg.textContent = "Welcome, " + response.username;
    
    //Workout reminder
    const d = new Date();
    let daysofweek = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];
    let today = daysofweek[d.getDay()];
    response = await window.fetch("/getschedule");
    response = await response.json();
    console.log(response.schedule);
    workoutreminder.innerHTML += "<b>Today's workout(s):</b>"
    if (response.schedule[today].length > 0) {
        for (let workout of response.schedule[today]) {
            if (workout[1] == response.username || workout[3].indexOf(response.username) > -1) {
                //Same deal as in Python - remove current user and redundant comma from output participants
                //If first line (let othetparticipants...) doesn't work, 2nd line does
                let otherparticipants = String(workout[3] + "," + workout[1]).replace(response.username + ",", "");
                otherparticipants = otherparticipants.replace("," + response.username, "")
                console.log(otherparticipants)
                if (otherparticipants.trim() == "") {
                    workoutreminder.innerHTML += `<li>${workout[2]} alone, ${workout[4]}-${workout[5]}</li>`;
                } else {
                    workoutreminder.innerHTML += `<li>${workout[2]} with ${otherparticipants}, ${workout[4]}-${workout[5]}</li>`;
                }
            }
        }
    } else {
        workoutreminder.innerHTML += " None! Enjoy your rest day, bro!"
    }
}
if (welcomemsg) {
    displaywelcome();
    for (let i of document.querySelectorAll("#cardcontainer button")) {
        i.addEventListener("click", function() {
            window.location.href = `${i.getAttribute("id").slice(0, -4)}.html`;
        })
    }
}

//profile.html
let usercard = document.querySelector("#usercard")
async function displayusercard() {
    let response = await window.fetch("/userdetails");
    response = await response.json();

    console.log(response.userdetails)
    let keys = ["Username", "Address", "Gym membership", "Style", "Deadlift record", "Squat record", "Benchpress record", "Overhead press record", "Schedule", "Volume lifted", "Time at gym"]
    for (let data of response.userdetails) {
        const label = keys[response.userdetails.indexOf(data)];
        labels.innerHTML += label + ":<br><br>";
        deets.innerHTML += data + "<br><br>"
    }
}
if (usercard) {
    displayusercard();
}

//notifications.html
let notifscontainer = document.querySelector("#notifscontainer")
async function displayrequests() {
    let request = await window.fetch("/getfriendreqs");
    request = await request.json();
    for (let wannabegymbro of request.data) {
        const notif = document.createElement("div.notif");
        notif.textContent = `You received a gymbro request from ${wannabegymbro}, bro!`;
        const accept = document.createElement("button");
        accept.classList.add("accept");
        accept.textContent = "Accept";
        const reject = document.createElement("button");
        reject.textContent = "Reject";
        reject.classList.add("reject");
        notif.appendChild(accept);
        notif.appendChild(reject);
        notifscontainer.appendChild(notif);

        accept.addEventListener("click", function() {
            window.fetch(`/processfriendreq?from=${wannabegymbro}&type=accept`);
            notif.innerHTML = "Request accepted";
        });

        reject.addEventListener("click", function() {
            window.fetch(`/processfriendreq?from=${wannabegymbro}&type=reject`);
            notif.innerHTML = "Request rejected";
        });
    }
    if (request.data.length == 0) {
        notifscontainer.innerHTML = "No notifications right now. Look at you, Mx Popular!"
    }
}
if (notifscontainer) {
    displayrequests();
}



//matches.html
let sortingcriterion = document.querySelector("#sortingcriterion");
if (sortingcriterion) {
    async function displaymatches() {
        response = await window.fetch(`/matches?crit=${sortingcriterion.value}`);
        response = await response.json();
        //Turn list into legible format
        let tablehtml = `<tr>
                            <th>Username</th>
                            <th>Coordinates</th>
                            <th>Membership</th>
                            <th>Style</th>
                            <th>Deadlift</th>
                            <th>Squat</th>
                            <th>Benchpress</th>
                            <th>Overhead press</th>
                            <th>Schedule</th>`
        if (sortingcriterion.value != "[Select criterion]") {
            tablehtml += `<th>${sortingcriterion.value}</th>`
        }
        tablehtml += "<th>Request</th></tr>"
        matchestable.innerHTML = tablehtml;
        
        for (let record of response.matches) {
            const newRow = matchestable.insertRow();

            for (let value of record) {
                const cell = newRow.insertCell();
                cell.textContent = value;
            }
            
            //FRIEND REQUESTS
            const button = document.createElement("button");
            button.textContent = "Add friend";
            const friendreq_outcome = document.createElement("div");
            const buttoncell = document.createElement("td");
            buttoncell.appendChild(button);
            buttoncell.appendChild(friendreq_outcome);
            newRow.appendChild(buttoncell);
            button.addEventListener("click", async function() {
                //Get gymbro's username
                let hopefullygymbro = button.parentNode.parentNode.querySelector("td").textContent;
                console.log(hopefullygymbro, "requested")
                let response = await window.fetch(`/requestfriend?requested=${hopefullygymbro}`);
                response = await response.json();
                friendreq_outcome.textContent = response.outcome;
            })
        }
    }

    displaymatches();
    sortingcriterion.addEventListener("input", async function() {
        displaymatches()
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
            //Convert checkbox id to container div id (e.g. bench? -> benchdiv)
            let correspondingdiv = document.querySelector(`#${mycheckbox.getAttribute("id").slice(0,-1)+"div"}`)
            
            if (mycheckbox.checked) { 
                //If checkbox checked then increment counter and show corresponding input div
                howmanychecked += 1;
                correspondingdiv.style.display = "flex";
                correspondingdiv.style.justifyContent = "space-between";
            } else {
                //If checkbox has been unchecked then decrement hide corresponding input div
                howmanychecked -= 1;
                correspondingdiv.style.display = "none";
            }

            //Only show fieldset of text inputs if at least 1 checkbox is selected
            if (howmanychecked > 0) {
                textinputs.style.display = "flex";
            } else {
                textinputs.style.display = "none";
            }
        })
    }

    //Timer button functionality
    let timerbutton = document.querySelector("button#timer");
    let timespent = 0; //seconds, convert later to avoid abuse of rounding up minute
    let starttime = -1;
    let timer_running = false;
    timerbutton.addEventListener("click", function(event) {
        event.preventDefault();
        let now = new Date().getTime(); //Get current time
        timer_running = !timer_running; //Start/resume timer if not running/stop if running

        if (timer_running) { //Timer started/resumed
            starttime = now; //Set new reference start time
            timerbutton.textContent = "Stop timer"; //Clicking on timer again will stop it
        } else { //Timer paused
            let timediff = (now - starttime)/1000; //Time elapsed from last click 
            timespent += timediff; //Add time from last click to total timer
            console.log(timespent);
            timerbutton.textContent = "Resume timer"; //Clicking on timer again 
        }
    })

    //Actual functionality of form
    submitworkout.addEventListener("click", async function(event) {
        event.preventDefault();
        msg.textContent = "";
        let sessionrecords = {};
        let sessionvolume = 0;

        for (let exercise of ["deadlift", "squat", "bench", "overhead", "otherlift"]) {
            let allsets = document.querySelector(`#${exercise}`).value; //Get all sets of current lift (deadlift or squat or etc.) - e.g. "3x80, 4x90"
            allsets = allsets.split(","); //Convert from string to list of sets (e.g. [3x80,4x90])

            let allweights = []; //Stores all weights lifted (e.g. [80, 90])
            for (let set of allsets) { //Iterate through the sets
                allweights.push(set.split("x")[1]); //Push only weight to array allweights (e.g. set is 3x80, 80 is pushed to allweights)

                //Add volume of each set to total weight lifted in session (e.g. 3x80 = 240)
                if (!isNaN(set.replaceAll(" ", "").replace("x", "")) && set.indexOf("x") > -1) { /*Only eval if set is 2 numbers and a x (and whitespace)
                Do not eval something like "abc*def" to avoid sessionvolume += undefined (and ending up with sessionvolume=NaN)*/
                    if (eval(set.replace("x", "*").replaceAll(" ", ""))) { //Check if set can be eval'd (e.g. "1233x" passes the previous check but can't be eval'd)
                        sessionvolume += eval(set.replace("x", "*").replaceAll(" ", "")); //Replace x with multiplication operator *, remove whitespace
                    }
                }
            }

            //Find largest item in allweights and save as session record for that lift
            //Example when exercise = "deadlift"
            //allweights = [90, 80, 95, 67]
            //sessionrecords = {"deadlift": 95, ...}
            sessionrecords[exercise] = Number(allweights.reduce((max, current) => (current > max ? current : max), allweights[0]));
            
            /*If there are no sets completed, set sessionrecords[lift] to -1 so that it isn't undefined (will cause error in backend otherwise)
            because the session records will be compared to all-time records in backend regardless of input */
            if (!sessionrecords[exercise]) {
                sessionrecords[exercise] = -1; //Current all-time record > -1 so all-time record will stay the same
            }
        }

        //Convert timespent from seconds to minutes, bump up by 1 to include incomplete mins (e.g. 40m50s = 41m)
        timespent = Math.floor(timespent/60) + 1;

        if (timer_running) {
            msg.textContent = "Hey broski, stop the timer, man!"
        } else {
            let response = await window.fetch(`/workout?records=${JSON.stringify(sessionrecords)}&volume=${sessionvolume}&timespent=${timespent}`);
            response = await response.json();
            
            if (response["new records"].length > 0) {
                msg.innerHTML = "Congrats, dude, you totally, like, crushed it with new personal record(s) in: " + response["new records"] + "! <br>Radical!"
            } else {
                msg.textContent = "No new records today, major bummer. Keep pushing, bro!"
            }
            gohome2.style.visibility = "visible";
        }
    })
}



//leaderboards.html
let sortleaderboardby = document.querySelector("#sortleaderboardby");
if (sortleaderboardby) {
    async function addleaderboardcells() {
        //Choose either global or friends-only leaderboard
        let leaderboardscale = document.querySelector("input[name='scale']:checked").getAttribute("id").slice(5);
        console.log(sortleaderboardby.value)
        //Fetch table ordered by chosen criterion and add row of cells for every record
        let response = await window.fetch(`/leaderboards?criterion=${sortleaderboardby.value}&scale=${leaderboardscale}`);
        response = await response.json();
        console.log(response.data)
        for (let record of response.data) {
            const newRow = leaderboardtable.insertRow();

            for (let value of record) {
                const cell = newRow.insertCell();
                cell.textContent = value;
            }
        }
    }
    function updateleaderboard() {
        //Clear current table to avoid duplicates, then sort leaderboard by new criterion
        leaderboardtable.innerHTML = `<tr>
                                        <th>Username</th>
                                        <th>Deadlift</th>
                                        <th>Squat</th>
                                        <th>Benchpress</th>
                                        <th>Overhead press</th>
                                        <th>Lower body total</th>
                                        <th>Upper body total</th>
                                        <th>Big lift total</th>
                                        <th>Volume lifted</th>
                                        <th>Time spent at the gym</th>
                                    </tr>`
        addleaderboardcells();

        //Highlight the sorting criterion
        //But don't highlight if sorting by username
        const sortingcriteria = ["", "deadlift", "squat", "bench", "overhead", "lowerbody", "upperbody", "bigtotal", "volume", "timespent"];
        if (sortleaderboardby.value != "username") {
            let column2behighlighted = sortingcriteria.indexOf(sortleaderboardby.value);
            let tableheadings = leaderboardtable.querySelector("tr").querySelectorAll("th");
            tableheadings[column2behighlighted].style.backgroundColor = "blue";
        }

        //Colour rows (DOESN'T RUN???? VOLVO PLS FIX)
        let datarows = leaderboardtable.querySelectorAll("tr:not(:first-child)");
        for (let row of datarows) {
            console.log("hello");
            let cells = row.querySelectorAll("td");
            console.log(cells[5].textContent);
            cells[5].style.backgroundColor = "blue";
        }
    }
    //Update leaderboard display
    addleaderboardcells();
    radioglobal.addEventListener("click", updateleaderboard);
    radiofriendsonly.addEventListener("click", updateleaderboard);
    //Change leaderboard sort factor
    sortleaderboardby.addEventListener("input", updateleaderboard);
}

//schedule.html
let scheduletable = document.querySelector("#scheduletable>tbody");
async function displayschedule() {
    let response = await window.fetch("/getschedule");
    response = await response.json();
    let daycells = document.querySelector("tr").children; //select all cells in 1st row of schedule (weekday names)
    let datacells = Array.from(document.querySelector("tr:last-child").children); //select all cells in 2nd row of schedule table (below weekday names)
    let daysofweek = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"];
    console.log(response.schedule)
    for (let cell of datacells) {
        //response.schedule is an object - there is a 2D array of workouts (which are 1D arrays) scheduled for every day of the week
        /*e.g. {
            Wednesday: [[ 10, "mikolajszywala", "benchpress,overhead,squat", … ], [ 15, "mikolajszywala", "deadlift", … ]]
            Friday: [[ 11, "mikolajszywala", "benchpress,overhead,squat", … ]]
        }
        */

        //Convert index of current cell to name of weekday (e.g. cell of index 2 is Wednesday, so get response.schedule["Wednesday"])
        //workoutsforday = response.schedule["Wednesday"] 
            // = [[ 10, "mikolajszywala", "benchpress,overhead,squat", … ], [ 15, "mikolajszywala", "deadlift", … ]]
        let workoutsforday = (response.schedule[daysofweek[datacells.indexOf(cell)]]); 
        let labels = ["Organiser: ", "Exercises: ", "Partners: ", "Start time: ", "End time: "] //Labels that will be added to the workout element
        for (let workout of workoutsforday) { //Iterate through 2D array - each workout is a 1D list
            if (workout) {
                let workoutdiv = document.createElement("div");
                //Set ID of div to workoutID so you know which workout to delete when 'x' clicked
                workoutdiv.setAttribute("id", workout[0]);
                workoutdiv.classList.add("workoutdiv"); //Add class "workoutdiv" for styling

                //deetsdiv is the text portion of the workout div (part without the remove button)
                let deetsdiv = document.createElement("div"); 
                workout = workout.slice(1); //Remove workoutID from workout list so it isn't displayed (unnecessary)
                for (let detail of workout) { //Iterate through 1D list (e.g. [ 10, "mikolajszywala", "benchpress,overhead,squat", … ])
                    let mylabel = labels[workout.indexOf(detail)]; //Get label corresponding to the detail (e.g. "Organiser:" "mikolajszywala")
                    
                    //If there are no workout partners, display "none" instead of literally nothing
                    let detailtodisplay = detail; //Have to make new variable "detailtodisplay", 
                                                //as changing "detail" doesn't actually change the element in the 1D array (needed on line 527) 
                    
                    if (mylabel == "Partners: " && detailtodisplay.length == 0) {
                        detailtodisplay = "<b>none</b>"
                    }
                    //Display labelled detail (e.g. Organiser: mikolajszywala)
                    deetsdiv.innerHTML += "<b>" + labels[workout.indexOf(detail)] + "</b>" + detailtodisplay + "<br>";
                }
                workoutdiv.appendChild(deetsdiv); 

                let removebtn = document.createElement("button");
                removebtn.classList.add("removebtn");
                removebtn.textContent = "×";
                removebtn.addEventListener("click", async function(){
                    let day = daycells[datacells.indexOf(cell)].textContent;
                    let response = await window.fetch(`/removefromschedule?workoutid=${workoutdiv.getAttribute("id")}`);
                    response = await response.json();
                    window.location.reload();
                })
                workoutdiv.appendChild(removebtn);
                cell.appendChild(workoutdiv);
            }
        }
        let addbtn = document.createElement("button");
        addbtn.textContent = "+";
        addbtn.addEventListener("click", function(){
            window.location.href = "/static/setschedule.html";
        })
        cell.appendChild(addbtn);
    }
}
if (scheduletable) {
    displayschedule();
}

//setschedule.html
let scheduleinput = document.querySelector("#scheduleinput");
async function displayfriends() {
    let response = await window.fetch("/getfriends");
    response = await response.json();
    for (let friend of response.friends) {
        let checkboxdiv = document.createElement("div");
        let checkbox = document.createElement(`input`);
        checkbox.setAttribute("id", friend);
        checkbox.setAttribute("name", friend);
        checkbox.setAttribute("type", "checkbox");
        let label = document.createElement("label");
        label.setAttribute("for", friend);
        label.textContent = friend;
        checkboxdiv.appendChild(checkbox);
        checkboxdiv.appendChild(label);
        partnerset.appendChild(checkboxdiv);
    }
}
async function addtoschedule(event) {
    event.preventDefault();
    let daysscheduled = whichselected(document.querySelectorAll("#scheduleset input"));
    let partners = whichselected(document.querySelectorAll("#partnerset input"));
    if (daysscheduled == "" || exerciselist.value.trim().length == 0 || starttime.value == "" || endtime.value == "" || endtime.value <= starttime.value) {
        msg.textContent = "Workout details invalid. Check again."
    } else {
        let response = await window.fetch(`/setschedule?days=${daysscheduled}&exercises=${exerciselist.value}&partners=${partners}&start=${starttime.value}&end=${endtime.value}`);
        response = await response.json();
        msg.textContent = response.data;
    }
}
if (scheduleinput) {
    displayfriends();
    submitbtn.addEventListener("click", addtoschedule)
}