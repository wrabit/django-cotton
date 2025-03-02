export default () => ({
    root: {
        ['x-id']() {
            return ['accordion-item'];
        },
    },
    trigger: {
        ['@click']() {
            return this.toggle();
        },
        [':aria-expanded']() {
            return this.$data.value.includes(this.$id('accordion-item'));
        },
        [':aria-controls']() {
            return this.$id('accordion-item') + '-content';
        },
        [':id']() {
            return this.$id('accordion-item') + '-trigger';
        },
        [':disabled']() {
            return this.$data.disabled;
        },
    },
    icon: {
        [':class']() {
            return { '-rotate-180': this.$data.value.includes(this.$id('accordion-item')) }
        }
    },
    content: {
        [':id']() {
            return this.$id('accordion-item') + '-content';
        },
        [':aria-labelledby']() {
            return this.$id('accordion-item') + '-trigger';
        },
        ['x-show']() {
            return this.$data.value.includes(this.$id('accordion-item'));
        },
        ['x-collapse.duration.300ms']() {
            return true;
        },
    },
    expand() {
        if (this.$data.type === 'single') {
            this.$data.value = this.$id('accordion-item')
        }
        this.$nextTick(() => { this.$dispatch('valueChange', { value: this.$data.value }) })
    },
    collapse() {
        if (this.$data.type === 'single' && this.collapsible) {
            this.$data.value = ''
        }
        this.$nextTick(() => { this.$dispatch('valueChange', { value: this.$data.value }) })
    },
    toggle() {
        this.$data.value.includes(this.$id('accordion-item')) ? this.collapse() : this.expand()
    }
})
