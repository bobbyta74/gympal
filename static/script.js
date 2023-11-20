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
//Every page defaults to dark mode on load
if (localStorage.getItem("displaymode") == "light") {
    document.body.classList.add("light-mode");
}
//Enable light/dark mode toggling
togglelightmode.addEventListener("click", function() {
    document.body.classList.toggle("light-mode");
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
        
        if (formvalid) {
            msg.textContent = "";
            let response = await window.fetch(`/register?username=${username.value.trim()}&pwd=${pwd.value}&address=${address.value.trim()}&membership=${membership.value}&style=${style}&deadlift=${deadlift.value}&squat=${squat.value}&bench=${bench.value}&&overhead=${overhead.value}&schedule=${myschedule}`);
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
                workoutreminder.innerHTML += `<li>${workout[2]} with ${otherparticipants}, ${workout[4]}-${workout[5]}</li>`;
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
    let keys = ["Username", "Address", "Gym membership", "Style", "Deadlift record", "Squat record", "Benchpress record", "Overhead press record", "Schedule", "Volume lifted this month", "Time at gym this month"]
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
            //Convert checkbox id to container div id
            //E.g. deadlift? -> deadliftdiv
            let correspondingdiv = document.querySelector(`#${mycheckbox.getAttribute("id").slice(0,-1)+"div"}`)
            
            //Add/subtract checked box counter and toggle visibility
            if (mycheckbox.checked) {
                howmanychecked += 1;
                correspondingdiv.style.display = "flex";
                correspondingdiv.style.justifyContent = "space-between";
            } else {
                howmanychecked -= 1;
                correspondingdiv.style.display = "none";
            }
            //Only show text inputs if at least 1 checkbox is selected
            if (howmanychecked > 0) {
                textinputs.style.display = "flex";
            } else {
                textinputs.style.visibility = "none";
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
                                        <th>Volume lifted this month</th>
                                        <th>Time spent at the gym this month</th>
                                    </tr>`
        addleaderboardcells();

        //Highlight the sorting criterion
        //But don't highlight if sorting by username
        const sortingcriteria = ["", "deadlift", "squat", "bench", "overhead", "lowerbody", "upperbody", "bigtotal", "monthsvolume", "monthstimespent"];
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
    let daycells = document.querySelector("tr").children;
    let datacells = Array.from(document.querySelector("tr:last-child").children);
    let daysofweek = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"];
    for (let cell of datacells) {
        let workoutsforday = (response.schedule[daysofweek[datacells.indexOf(cell)]]);
        let labels = ["Organiser: ", "Exercises: ", "Partners: ", "Start time: ", "End time: "]
        for (let workout of workoutsforday) {
            if (workout) {
                let newdiv = document.createElement("div");
                //Save workout number as ID of div for use in deleting workout/removing self from workout
                newdiv.setAttribute("id", workout[0]);
                newdiv.classList.add("workoutdiv");
                let deetsdiv = document.createElement("div");
                //Don't display numeric workout ID
                workout = workout.slice(1);
                for (let detail of workout) {
                    let mylabel = labels[workout.indexOf(detail)];
                    //If there are no workout partners, display "none" instead of literally nothing
                    let detailtodisplay = detail;
                    if (mylabel == "Partners: " && detailtodisplay.length == 0) {
                        detailtodisplay = "<b>none</b>"
                    }
                    deetsdiv.innerHTML += "<b>" + labels[workout.indexOf(detail)] + "</b>" + detailtodisplay + "<br>";
                }
                newdiv.appendChild(deetsdiv);

                let removebtn = document.createElement("button");
                removebtn.classList.add("removebtn");
                removebtn.textContent = "×";
                removebtn.addEventListener("click", async function(){
                    let day = daycells[datacells.indexOf(cell)].textContent;
                    let response = await window.fetch(`/removefromschedule?workoutid=${newdiv.getAttribute("id")}`);
                    response = await response.json();
                    window.location.reload();
                })
                newdiv.appendChild(removebtn);
                cell.appendChild(newdiv);
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
    let response = await window.fetch(`/setschedule?days=${daysscheduled}&exercises=${exerciselist.value}&partners=${partners}&start=${starttime.value}&end=${endtime.value}`);
    response = await response.json();
    msg.textContent = response.data;
    if (response.data == "success!") {
        window.location.href = "/static/schedule.html"
    }
}
if (scheduleinput) {
    displayfriends();
    submitbtn.addEventListener("click", addtoschedule)
}