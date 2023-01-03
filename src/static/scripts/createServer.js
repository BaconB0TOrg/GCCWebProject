// taken from https://www.youtube.com/watch?v=zbjGcA3iEME, Author: dcode

class CustomSelect {
    constructor(originalSelectElement){
        this.originalSelectElement = originalSelectElement;
        this.customSelect = document.createElement("div");
        this.customSelect.classList.add("select");

        this.originalSelectElement.querySelectorAll("option").forEach(optionElement => {
            const itemElment = document.createElement("div");

            itemElment.classList.add("select__item");
            itemElment.textContent = optionElement.textContent;
            this.customSelect.appendChild(itemElment);

            // if seleted by default then add the correct class to corelate to that
            if (optionElement.selected){
                this._select(itemElment);
            }

            itemElment.addEventListener("click", () => {
                if (itemElment.classList.contains("select__item--selected")){
                    this._deselect(itemElment);
                } else {
                    this._select(itemElment);
                }
            });
        });

        this.originalSelectElement.insertAdjacentElement("afterend", this.customSelect);
        this.originalSelectElement.style.display = "none";
    }

    _select(itemElment){
        const index = Array.from(this.customSelect.children).indexOf(itemElment); // finding the index of the child 
        
        this.originalSelectElement.querySelectorAll("option")[index].selected = true;
        itemElment.classList.add("select__item--selected");
    }

    _deselect(itemElment){
        const index = Array.from(this.customSelect.children).indexOf(itemElment); // finding the index of the child 
        
        this.originalSelectElement.querySelectorAll("option")[index].selected = false;
        itemElment.classList.remove("select__item--selected");
    }
}

// Helper function to set up an event listener that trasition between two divs
function trasition_event_fade(button, startingDiv, endingDiv){
    button.addEventListener("click", () => {
        // remove visible item css from the starting div
        startingDiv.classList.remove("visible__item");
        // hide the starting div and show the ending div
        startingDiv.classList.add("hidden__item"); // current div trasitioned out
        // remove the hidden item css from the ending div
        endingDiv.classList.remove("hidden__item");
        // add the visible item css to the ending div 
        endingDiv.classList.add("visible__item"); // next div trasitioned in
    });
}

// Helper function that toggles the dropdown of the div passed
function trasition_event_dropdown(button, div){
    button.addEventListener("click", () => {
        if(div.classList.contains("dropdown")){
            div.classList.remove("dropdown"); //remove dropdown
            div.classList.add("hide");
        } else {
            div.classList.remove("hide");
            div.classList.add("dropdown"); // add dropdown
        }
    });
}

window.addEventListener('DOMContentLoaded', (event) => {
    document.querySelectorAll(".custom-select").forEach(selectElement => {
        new CustomSelect(selectElement);
    });

    // Set up event listeners for the progression of the form
    // Div for sections of the form
    const tagDiv = document.getElementById("tag__form")
    const optionDiv = document.getElementById("options")
    const serverDiv = document.getElementById("server__config")
    const advOptions = document.getElementById("advanced__options")

    // Next Buttons
    const tagButton = document.getElementById("tag__next");
    const optionsButton = document.getElementById("options__next");

    // advanced options link
    const advLine = document.getElementById("adv")

    trasition_event_fade(tagButton ,tagDiv, optionDiv); 
    trasition_event_fade(optionsButton, optionDiv, serverDiv);
    
    trasition_event_dropdown(advLine, advOptions);
});