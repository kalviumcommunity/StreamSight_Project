def register_routes(app):
    from app.routes import (
        auth, users, videos, categories, watch, bookmarks,
        search, history, analytics, dashboard, admin, home,
    )

    app.register_blueprint(auth.bp)
    app.register_blueprint(users.bp)
    app.register_blueprint(videos.bp)
    app.register_blueprint(categories.bp)
    app.register_blueprint(watch.bp)
    app.register_blueprint(bookmarks.bp)
    app.register_blueprint(search.bp)
    app.register_blueprint(history.bp)
    app.register_blueprint(analytics.bp)
    app.register_blueprint(dashboard.bp)
    app.register_blueprint(admin.bp)
    app.register_blueprint(home.bp)
