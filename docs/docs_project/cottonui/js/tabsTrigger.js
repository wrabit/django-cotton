export default (value) => ({
    value: value,
    root: {
        ['@click']() {
            return this.setAsActive();
        },
        ['@focus']() {
            if (this.$data.activationMode != "manual") {
                this.setAsActive();
            }
        },
        [':aria-selected']() {
            return this.value == this.$data.active;
        },
        [':tabindex']() {
            return this.$data.active == this.value ? 0 : -1;
        },
        [':class']() {
            return { 'bg-background text-foreground shadow-sm': this.$data.active == this.value };
        },
        [':aria-labelledby']() {
            return this.$id('tab') + '-'+this.value+'-panel';
        },
        [':id']() {
            return this.$id('accordion-item') + '-trigger';
        },
    },
    setAsActive() {
        this.$data.active = this.value;
    }
})
