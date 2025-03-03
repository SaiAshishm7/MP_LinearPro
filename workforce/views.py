
from django.shortcuts import render, redirect
from django.views import View
from .models import OptimizationParameters, OptimizationResult
from .forms import OptimizationForm
import json

class OptimizationView(View):
    def get(self, request):
        # Get or create default parameters
        params, created = OptimizationParameters.objects.get_or_create(id=1)
        form = OptimizationForm(instance=params)
        
        # Get the latest result if it exists
        latest_result = OptimizationResult.objects.filter(parameters=params).last()
        
        # Generate sensitivity data for chart
        sensitivity_data = []
        if latest_result:
            for b in range(int(params.budget * 0.5), int(params.budget * 1.5), int(params.budget * 0.1)):
                result = self.solve_with_budget(params, b)
                sensitivity_data.append({
                    'budget': b,
                    'production': result['production']
                })
        
        context = {
            'form': form,
            'result': latest_result,
            'sensitivity_data': json.dumps(sensitivity_data),
        }
        
        return render(request, 'workforce/optimize.html', context)
    
    def post(self, request):
        # Get or create default parameters
        params, created = OptimizationParameters.objects.get_or_create(id=1)
        
        # Update parameters with form data
        form = OptimizationForm(request.POST, instance=params)
        if form.is_valid():
            params = form.save()
            
            # Solve the optimization problem
            solution = self.solve_workforce_optimization(params)
            
            # Create a new result object
            OptimizationResult.objects.create(
                parameters=params,
                skilled_workers=solution['skilled_workers'],
                semi_skilled_workers=solution['semi_skilled_workers'],
                total_production=solution['total_production'],
                budget_used=solution['budget_used'],
            )
            
            return redirect('optimize')
        
        context = {
            'form': form,
        }
        
        return render(request, 'workforce/optimize.html', context)
    
    def solve_workforce_optimization(self, params):
        """
        Solve the workforce optimization problem using the provided parameters.
        Uses a linear programming approach to maximize production subject to constraints.
        """
        # Define all possible corner points of the feasible region
        corner_points = []
        
        # Origin
        corner_points.append((0, 0))
        
        # Budget constraint line: skilled_cost*x + semi_skilled_cost*y = budget
        # Intersections with axes
        if params.skilled_cost > 0:
            corner_points.append((params.budget / params.skilled_cost, 0))
        if params.semi_skilled_cost > 0:
            corner_points.append((0, params.budget / params.semi_skilled_cost))
        
        # Budget constraint intersections with availability constraints
        if params.skilled_cost > 0 and params.semi_skilled_cost > 0:
            # Intersection with x = max_skilled_workers
            y = (params.budget - params.skilled_cost * params.max_skilled_workers) / params.semi_skilled_cost
            if y >= 0:
                corner_points.append((params.max_skilled_workers, y))
            
            # Intersection with y = max_semi_skilled_workers
            x = (params.budget - params.semi_skilled_cost * params.max_semi_skilled_workers) / params.skilled_cost
            if x >= 0:
                corner_points.append((x, params.max_semi_skilled_workers))
        
        # Production constraint line: skilled_production*x + semi_skilled_production*y = min_production
        # Intersections with axes
        if params.skilled_production > 0:
            corner_points.append((params.min_production / params.skilled_production, 0))
        if params.semi_skilled_production > 0:
            corner_points.append((0, params.min_production / params.semi_skilled_production))
        
        # Production constraint intersections with availability constraints
        if params.skilled_production > 0 and params.semi_skilled_production > 0:
            # Intersection with x = max_skilled_workers
            y = (params.min_production - params.skilled_production * params.max_skilled_workers) / params.semi_skilled_production
            if y >= 0:
                corner_points.append((params.max_skilled_workers, y))
            
            # Intersection with y = max_semi_skilled_workers
            x = (params.min_production - params.semi_skilled_production * params.max_semi_skilled_workers) / params.skilled_production
            if x >= 0:
                corner_points.append((x, params.max_semi_skilled_workers))
        
        # Add max skilled/semi-skilled workers point
        corner_points.append((params.max_skilled_workers, params.max_semi_skilled_workers))
        
        # Filter valid corners that satisfy all constraints
        valid_corners = []
        for x, y in corner_points:
            # Non-negativity constraint
            if x < 0 or y < 0:
                continue
                
            # Maximum availability constraint
            if x > params.max_skilled_workers or y > params.max_semi_skilled_workers:
                continue
                
            # Budget constraint
            if params.skilled_cost * x + params.semi_skilled_cost * y > params.budget:
                continue
                
            # Minimum production constraint
            if params.skilled_production * x + params.semi_skilled_production * y < params.min_production:
                continue
                
            valid_corners.append((x, y))
        
        # Find corner with maximum production
        best_x = 0
        best_y = 0
        max_production_value = 0
        
        for x, y in valid_corners:
            production = params.skilled_production * x + params.semi_skilled_production * y
            if production > max_production_value:
                max_production_value = production
                best_x = x
                best_y = y
        
        # Round to nearest integer (workforce must be whole numbers)
        best_x = int(round(best_x))
        best_y = int(round(best_y))
        
        # Handle case when no valid corners were found (infeasible problem)
        if not valid_corners:
            # Try to find a solution that minimizes the constraint violations
            # For simplicity, we'll just use the maximum possible workforce
            best_x = params.max_skilled_workers
            best_y = params.max_semi_skilled_workers
        
        # Recalculate with rounded values
        actual_production = params.skilled_production * best_x + params.semi_skilled_production * best_y
        actual_budget_used = params.skilled_cost * best_x + params.semi_skilled_cost * best_y
        
        return {
            'skilled_workers': best_x,
            'semi_skilled_workers': best_y,
            'total_workers': best_x + best_y,
            'total_production': actual_production,
            'budget_used': actual_budget_used,
            'budget_remaining': params.budget - actual_budget_used,
        }
    
    def solve_with_budget(self, params, test_budget):
        """
        Perform sensitivity analysis by solving with a test budget.
        Returns the optimal solution for the given budget.
        """
        # We'll use a simpler approach for sensitivity analysis
        # Determine ratios of production/cost for each worker type
        skilled_efficiency = params.skilled_production / params.skilled_cost
        semi_skilled_efficiency = params.semi_skilled_production / params.semi_skilled_cost
        
        # Allocate budget to more efficient worker type first
        skilled_workers = 0
        semi_skilled_workers = 0
        
        if skilled_efficiency >= semi_skilled_efficiency:
            # Skilled workers are more efficient, prioritize them
            skilled_workers = min(params.max_skilled_workers, test_budget // params.skilled_cost)
            remaining_budget = test_budget - skilled_workers * params.skilled_cost
            semi_skilled_workers = min(params.max_semi_skilled_workers, remaining_budget // params.semi_skilled_cost)
        else:
            # Semi-skilled workers are more efficient, prioritize them
            semi_skilled_workers = min(params.max_semi_skilled_workers, test_budget // params.semi_skilled_cost)
            remaining_budget = test_budget - semi_skilled_workers * params.semi_skilled_cost
            skilled_workers = min(params.max_skilled_workers, remaining_budget // params.skilled_cost)
        
        # Calculate production
        production = params.skilled_production * skilled_workers + params.semi_skilled_production * semi_skilled_workers
        
        # Check if minimum production constraint is met
        if production < params.min_production:
            # If not, try to find a feasible solution
            # This is a simplification - a real solver would use a more sophisticated approach
            
            # Try various combinations until we find one that meets the minimum production
            best_production = 0
            best_skilled = 0
            best_semi = 0
            
            for s in range(min(params.max_skilled_workers + 1, (test_budget // params.skilled_cost) + 1)):
                remaining = test_budget - s * params.skilled_cost
                sm = min(params.max_semi_skilled_workers, remaining // params.semi_skilled_cost)
                
                prod = s * params.skilled_production + sm * params.semi_skilled_production
                
                if prod >= params.min_production and prod > best_production:
                    best_production = prod
                    best_skilled = s
                    best_semi = sm
            
            return {
                'skilled': best_skilled,
                'semi_skilled': best_semi,
                'production': best_production if best_production > 0 else 0
            }
        
        return {
            'skilled': skilled_workers,
            'semi_skilled': semi_skilled_workers,
            'production': production
        }
