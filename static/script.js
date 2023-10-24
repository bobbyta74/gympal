//Using if statements allow me to use the same script for different pages
//Avoids error: x is undefined
submitlogin = document.querySelector("#submitlogin");
//If submitlogin exists on this page, attempt login
if (submitlogin) {
    submitlogin.addEventListener("click", async function(event) {
        //Avoid refreshing page
        event.preventDefault();
        //Take username and password from input fields, send to app.py and wait for it to respond
        let response = await window.fetch(`/login?username=${username.value.trim()}&password=${pwd.value}`);
        response = await response.json()
        console.log(response)
        if (response.type == "success") {
            msg.textContent = "Login successful";
            console.log("Login successful")
        } else if (response.type == "failure") {
            msg.textContent = "Login failed";
        } else {
            console.log("not working")
        }
    })
}

submitregister = document.querySelector("#submitregister")
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
        myschedule = myschedule.slice(0, -1);

        //Check which style is selected and set mystyle to that
        let mystyle = "";
        //CONTINUE THIS ONE
        
        let response = await window.fetch(`/register?username=${username.value.trim()}&pwd=${pwd.value}&coords=${coords.value.trim()}&membership=${membership.value}&style=${mystyle}&deadlift=${deadlift.value}&squat=${squat.value}&bench=${bench.value}&&overhead=${overhead.value}`)
    })
}
