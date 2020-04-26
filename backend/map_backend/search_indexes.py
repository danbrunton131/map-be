from haystack import indexes
from .models import Course

class CourseIndex(indexes.SearchIndex, indexes.Indexable):
	text = indexes.EdgeNgramField(document=True, use_template=True)

	def get_model(self):
		return Course

	def index_queryset(self, using=None):
		""" Used for indexing """
		return self.get_model().objects.all()