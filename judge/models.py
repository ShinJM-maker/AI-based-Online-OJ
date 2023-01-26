from django.db import models
from django.urls import reverse
from django.core.cache import cache
from django.core.validators import RegexValidator,MaxValueValidator,MinValueValidator
from django.utils.functional import cached_property
from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _
from django.conf import settings

# Create your models here.
class Problem(models.Model):
    code = models.CharField(max_length=20, verbose_name=_('problem code'), unique=True,
                            validators=[RegexValidator('^[a-z0-9]+$', _('Problem code must be ^[a-z0-9]+$'))],
                            help_text=_('These are code!'))#'A short, unique code for the problem, ''used in the url after /problem/'))
    name = models.CharField(max_length=100, verbose_name=_('problem name'), db_index=True,
                            help_text=_('These are full name of the problem'))#'The full name of the problem, ''as shown in the problem list.'))                           
    description = models.TextField(verbose_name=_('problem Description'))
    time_limit = models.FloatField(verbose_name=_('time limit'),
                                   help_text=_('The time limit for this problem, in seconds. '
                                               'Fractional seconds (e.g. 1.5) are supported.'),default=settings.DMOJ_PROBLEM_MIN_TIME_LIMIT,
                                   validators=[MinValueValidator(settings.DMOJ_PROBLEM_MIN_TIME_LIMIT),
                                               MaxValueValidator(settings.DMOJ_PROBLEM_MAX_TIME_LIMIT)])
    memory_limit = models.PositiveIntegerField(verbose_name=_('memory limit'),
                                               help_text=_('The memory limit for this problem, in kilobytes '
                                                           '(e.g. 64mb = 65536 kilobytes).'),
                                                default=settings.DMOJ_PROBLEM_MIN_MEMORY_LIMIT,
                                               validators=[MinValueValidator(settings.DMOJ_PROBLEM_MIN_MEMORY_LIMIT),
                                                           MaxValueValidator(settings.DMOJ_PROBLEM_MAX_MEMORY_LIMIT)])
    #short_circuit = models.BooleanField(default=False)
    points = models.FloatField(verbose_name=_('points'),
                               help_text=_('Points awarded for problem completion. '
                                           "Points are displayed with a 'p' suffix if partial."),
                                default=settings.DMOJ_PROBLEM_MIN_PROBLEM_POINTS,
                               validators=[MinValueValidator(settings.DMOJ_PROBLEM_MIN_PROBLEM_POINTS)])
    #types = models.ManyToManyField(ProblemType, verbose_name=_('problem types'),
    #                            help_text=_('The type of problem, '
    #                                        "as shown on the problem's page."))
    #partial = models.BooleanField(verbose_name=_('allows partial points'))
    #allowed_languages = models.ManyToManyField(Language, verbose_name=_('allowed languages'),
    #                                           help_text=_('List of allowed submission languages.'))
    #is_public = models.BooleanField(verbose_name=_('publicly visible'), db_index=True, default=False)
    #is_manually_managed = models.BooleanField(verbose_name=_('manually managed'), db_index=True, default=False,
    #                                          help_text=_('Whether judges should be allowed to manage data or not.'))
    #date = models.DateTimeField(verbose_name=_('date of publishing'), null=True, blank=True, db_index=True,
    #                            help_text=_("Doesn't have magic ability to auto-publish due to backward compatibility"))
    #og_image = models.CharField(verbose_name=_('OpenGraph image'), max_length=150, blank=True)
    #summary = models.TextField(blank=True, verbose_name=_('problem summary'),
    #                           help_text=_('Plain-text, shown in meta description tag, e.g. for social media.'))
    #user_count = models.IntegerField(verbose_name=_('number of users'), default=0,
    #                                 help_text=_('The number of users who solved the problem.'))
    #ac_rate = models.FloatField(verbose_name=_('solve rate'), default=0)
    #is_full_markup = models.BooleanField(verbose_name=_('allow full markdown access'), default=False)
    #objects = TranslatedProblemQuerySet.as_manager()
    #tickets = GenericRelation('Ticket')
    def __init__(self, *args, **kwargs) :
        super(Problem, self).__init__(*args,**kwargs)
        self.__original_code = self.code

    #def languages_list(self):
    #    return self.allowed_languages.values_list('common_name', flat=True).distinct().order_by('common_name')
    
    #cached_property는 처음 호출된 Property 함수 결과값을 캐싱해둔다. 그리고 이후에는 캐싱된 결과값을 리턴한다.
    @classmethod
    def get_problems(cls):
        return cls.objects.defer('description')

    def __str__ (self):
        return self.name

    def get_absolute_url(self):
        return reverse('problem_detail',args=(self.code,))
    
    #@property
    #def usable_languages(self):
    #    return self.allowed_languages.filter(judges__in=self.judges.filter(online=True)).distinct()
    
   

    @property
    def language_time_limit(self):
        key = 'problem_tls:%d' % self.id
        result = cache.get(key)
        if result is not None:
            return result
        result = self._get_limits('time_limit')
        cache.set(key, result)
        return result

    @property
    def language_memory_limit(self):
        key = 'problem_mls:%d' % self.id
        result = cache.get(key)
        if result is not None:
            return result
        result = self._get_limits('memory_limit')
        cache.set(key, result)
        return result


    def save(self, *args, **kwargs):
        super(Problem, self).save(*args, **kwargs)
        if self.code != self.__original_code:
            try:
                problem_data = self.data_files
            except AttributeError:
                pass
            else:
                problem_data._update_code(self.__original_code, self.code)

    save.alters_data = True
    class Meta:
        verbose_name = _('problem')

