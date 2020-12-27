from django import forms

from tasks.models import Project, Sprint, Task


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = '__all__'

    def clean(self):
        super(ProjectForm, self).clean()
        deadline = self.cleaned_data.get('date_end', '')
        redline = self.cleaned_data.get('redline', '')

        if redline and deadline and redline > deadline:
            raise forms.ValidationError("Deadline must be greater (or equal) than Redline (`To be completed`)")
        return self.cleaned_data


class SprintForm(forms.ModelForm):
    class Meta:
        model = Sprint
        fields = '__all__'

    def clean(self):
        super(SprintForm, self).clean()
        deadline = self.cleaned_data.get('date_end', '')
        redline = self.cleaned_data.get('redline', '')

        if redline and deadline and redline > deadline:
            raise forms.ValidationError("Deadline must be greater (or equal) than Redline (`To be completed`)")
        return self.cleaned_data


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = '__all__'

    def clean(self):
        super(TaskForm, self).clean()
        deadline = self.cleaned_data.get('deadline', '')
        redline = self.cleaned_data.get('redline', '')

        if redline and deadline and redline > deadline:
            raise forms.ValidationError("Deadline must be greater (or equal) than Redline (`To be completed`)")
        return self.cleaned_data
