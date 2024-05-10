from app.web.mixins import AdminOnlyMixin, ViewMixin


class ShareAddView(AdminOnlyMixin, ViewMixin):
    pass


class ShareDeleteView(AdminOnlyMixin, ViewMixin):
    pass
