export default (name, initialValue = null) => ({
    value: initialValue,
    name: name,

    init() {
        // Initialize value from checked option if not provided
        if (this.value === null) {
            const checkedInput = this.$el.querySelector('input[type="radio"]:checked');
            if (checkedInput) {
                this.value = checkedInput.value;
            }
        }
    },

    select(optionValue) {
        this.value = optionValue;
        this.$dispatch('change', { value: optionValue });
    },

    isSelected(optionValue) {
        return this.value === optionValue;
    },

    selectNext() {
        const radios = Array.from(this.$el.querySelectorAll('[role="radio"]:not([aria-disabled="true"])'));
        const currentIndex = radios.findIndex(r => r === document.activeElement);

        if (currentIndex === -1) return;

        const nextIndex = (currentIndex + 1) % radios.length;
        radios[nextIndex].focus();
        this.select(radios[nextIndex].dataset.value);
    },

    selectPrevious() {
        const radios = Array.from(this.$el.querySelectorAll('[role="radio"]:not([aria-disabled="true"])'));
        const currentIndex = radios.findIndex(r => r === document.activeElement);

        if (currentIndex === -1) return;

        const prevIndex = currentIndex === 0 ? radios.length - 1 : currentIndex - 1;
        radios[prevIndex].focus();
        this.select(radios[prevIndex].dataset.value);
    },

    hasRovingTabindex(optionValue) {
        // Roving tabindex pattern: selected option or first option gets tabindex="0"
        if (this.value === optionValue) return true;

        // If nothing selected, first option gets focus
        const radios = Array.from(this.$el.querySelectorAll('[role="radio"]:not([aria-disabled="true"])'));
        if (!this.value && radios[0] && radios[0].dataset.value === optionValue) return true;

        return false;
    }
})
