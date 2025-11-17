export default (initialTab = null, activationMode = "automatic") => ({
    active: initialTab,
    activationMode: activationMode,

    init() {
        if (this.active === null) {
            // Get first tab value
            const firstTab = this.$el.querySelector('[data-tab-value]');
            if (firstTab) {
                this.active = firstTab.dataset.tabValue;
            }
        }
    }
})
