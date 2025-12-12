export default (name, initialValues = []) => ({
    values: Array.isArray(initialValues) ? initialValues : [],
    name: name,

    init() {
        // Initialize values from checked checkboxes if not provided
        if (this.values.length === 0) {
            const checkedInputs = this.$el.querySelectorAll('input[type="checkbox"]:checked');
            this.values = Array.from(checkedInputs).map(input => input.value);
        }
    },

    toggle(optionValue) {
        if (this.isChecked(optionValue)) {
            this.values = this.values.filter(v => v !== optionValue);
        } else {
            this.values.push(optionValue);
        }
        this.$dispatch('change', { values: this.values });
    },

    isChecked(optionValue) {
        return this.values.includes(optionValue);
    }
})
