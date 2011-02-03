# begin monkey patching of pyblog
# assumed safe because pyblog hasn't been updated in 18 months
import pyblog

def monkeypatch_method(cls):
    def decorator(func):
        setattr(cls, func.__name__, func)
        return func
    return decorator

@monkeypatch_method(pyblog.WordPress)
def get_tags(self, blogid=1):
    return self.execute('wp.getTags', blogid, self.username, self.password)