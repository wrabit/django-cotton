export default () => ({
    subOpen: false,
    subPreview: false,
    root: {
        ['@keydown.escape']() {
            return this.closeSub();
        },
        ['@click.outside']() {
            return this.closeSub();
        },
        ['@keydown.right']() {
            return this.open();
        },
        [':aria-expanded']() {
            return this.subOpen;
        },
        ['@mouseleave']() {
            this.closePreview();
        },
    },
    trigger: {
        ['@click.capture.stop']() {
            return this.open();
        },
        ['@mouseenter']() {
            this.openPreview();
            this.$focus.focus(this.$el);
        },
        ['@focus']() {
            this.$el.setAttribute('tabindex', 0)
        },
        ['@focusout']() {
            this.$el.setAttribute('tabindex', -1)
        },
    },
    template: {
        ['x-if']() {
            return this.subOpen || this.subPreview;
        },
    },
    content: {
        ['x-anchor.right-start.no-style']() {
            return this.$refs.subTrigger;
        },
        [':style']() {
            let correction = 0
            if (this.$anchor.x + this.$refs.content.scrollWidth > window.innerWidth) {
                correction = this.$refs.content.getBoundingClientRect().width / 2
            }
            else if (this.$anchor.x - this.$refs.subTrigger.getBoundingClientRect().width <= 0) {
                correction = -this.$refs.content.getBoundingClientRect().width
            }
            return { position: 'absolute', top: this.$anchor.y + 'px', left: this.$anchor.x - correction + 'px' };
        },
        ['x-trap']() {
            return this.subOpen;
        },
        ['x-show']() {
            return this.subOpen || this.subPreview;
        },
        ['x-transition']() {
            return true;
        },
        ['x-cloak']() {
            return true;
        },
        ['@keydown.down.prevent']() {
            return this.$focus.wrap().next();
        },
        ['@keydown.up.prevent']() {
            return this.$focus.wrap().previous();
        },
        ['@keydown']($event) {
            if ($event.key == 'Home') {
                return this.$focus.wrap().first();
            }
            if ($event.key == 'End') {
                return this.$focus.wrap().last();
            }
        },
        ['@keydown.left.stop']() {
            return this.closeSub();
        },
    },
    menuItem: {
        ['@click']() {
            this.closeSub();
            this.$data.close()
        },
        ['@mouseover']() {
            return this.$focus.focus(this.$el);
        },
        [':tabindex']() {
            (this.subOpen || this.subPreview) && this.$el.isEqualNode(this.$root.querySelectorAll('button')[2]) ? 0 : -1
        },
        ['@focus']() {
            this.$el.setAttribute('tabindex', 0)
        },
        ['@focusout']() {
            this.$el.setAttribute('tabindex', -1)
        },
        ['@keydown.tab']() {
            this.closeSub()
        },
    },
    open() {
        this.subOpen = true
    },
    closeSub() {
        this.subOpen = false
    },
    toggle() {
        this.subOpen == true ? this.closeSub() : this.open()
    },
    openPreview() {
        if (window.innerWidth <= 640) {  // no previews on mobile boohoo
            return
        }
        this.subPreview = true;
    },
    closePreview() {
        this.subPreview = false;
    }
})
