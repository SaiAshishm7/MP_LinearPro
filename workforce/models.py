
from django.db import models

class OptimizationParameters(models.Model):
    skilled_cost = models.FloatField(default=300)
    semi_skilled_cost = models.FloatField(default=150)
    skilled_production = models.FloatField(default=10)
    semi_skilled_production = models.FloatField(default=4)
    budget = models.FloatField(default=6000)
    min_production = models.FloatField(default=100)
    max_skilled_workers = models.IntegerField(default=30)
    max_semi_skilled_workers = models.IntegerField(default=60)
    
    def __str__(self):
        return f"Optimization Parameters (ID: {self.id})"

class OptimizationResult(models.Model):
    parameters = models.ForeignKey(OptimizationParameters, on_delete=models.CASCADE)
    skilled_workers = models.IntegerField()
    semi_skilled_workers = models.IntegerField()
    total_production = models.FloatField()
    budget_used = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Result: {self.skilled_workers} skilled, {self.semi_skilled_workers} semi-skilled"
