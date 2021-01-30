:noindex:
:orphan:

API reference
=============

This page holds mloq API documentation, which might be helpful for final
users or developers to create their own mloq-based utilities. Among the
different sub-packages and modules, we might differentiate two big categories:
core utilities and high-level ones.


* **Core API:** This routines are locate within the `mloq.api` that show the different features of the library can be accessed programmatically.



.. toctree::
   :maxdepth: 5

   {% for page in pages %}
   {% if page.top_level_object and page.display %}
   {{ page.include_path }}
   {% endif %}
   {% endfor %}