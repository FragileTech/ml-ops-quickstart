# What mloq generated for your project

{% for file, description in generated_files %}* `{{ file }}` - {{ description }}
{% endfor %}