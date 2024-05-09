from app.web.mixins import ViewMixin, AdminOnlyMixin


class ShareAddView(AdminOnlyMixin, ViewMixin):
    pass

class ShareDeleteView(AdminOnlyMixin, ViewMixin):
    pass
