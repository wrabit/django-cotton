from django.template.backends.django import DjangoTemplates


class CottonTemplates(DjangoTemplates):
    def __init__(self, params):
        super().__init__(params)

        # Create a new CottonLoader instance
        # cotton_loader = CottonLoader(self.engine)

        # Wrap the CottonLoader with a CachedLoader
        # cached_cotton_loader = CachedLoader(self.engine, [cotton_loader])

        # Insert the cached Cotton loader at the beginning of the loaders list
        # self.engine.loaders.insert(0, cached_cotton_loader)

        print(self.engine.loaders)

        self.engine.loaders.insert(0, "django_cotton.cotton_loader.Loader")
