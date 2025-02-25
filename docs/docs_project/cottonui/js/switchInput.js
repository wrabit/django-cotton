export default (disabled) => ({
    switchOn: false,
    disabled: disabled,
    root: {
        [':aria-checked']() {
            return this.switchOn;
        },
        [':aria-labelledby']() {
            if (this.$refs.input?.labels[0]?.id ?? false) {
                return this.$refs.input.labels[0].id;
            }
        },
        [':aria-label']() {
            if (this.$refs.input?.labels[0].innerText ?? false) {
                return this.$refs.input.labels[0].innerText;
            }
        },
    },
    input: {
        ['x-model.boolean']() {
            return "switchOn";
        },
        ['x-ref']() {
            return "input";
        },
        [':disabled']() {
            return this.disabled;
        },
    },
    trigger: {
        ['@click']() {
            return this.toggle()
        },
        ['x-cloak']() {
            return true;
        },
    },
    setSwitchState(value) {
        if (this.disabled) {
            return;
        }

        this.switchOn = value;
        this.$refs.input.checked = value;
        this.$dispatch('checkedChange');
    },
    toggle() {
        this.setSwitchState(!this.switchOn);
    }
})
