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

window.addEventListener('DOMContentLoaded', (event) => {
    document.querySelectorAll(".custom-select").forEach(selectElement => {
        new CustomSelect(selectElement);
    });
});