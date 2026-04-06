import datetime
import json

def generate_roadmap(features, tech_stack, timeline):
    """Generates a project roadmap based on features, tech stack, and timeline."""
    roadmap = {
        'project': 'scripts',
        'tech_stack': tech_stack,
        'features': features,
        'timeline': timeline,
        'generated_on': datetime.datetime.now().strftime('%Y-%m-%d')
    }
    
    # Organize features by tech stack
    organized_features = {}
    for feature in features:
        for tech in tech_stack:
            if tech in feature['tech']:
                if tech not in organized_features:
                    organized_features[tech] = []
                organized_features[tech].append(feature['name'])
                break
    
    roadmap['organized_features'] = organized_features
    
    # Export roadmap as JSON
    with open('roadmap.json', 'w') as f:
        json.dump(roadmap, f, indent=4)
    
    print('Roadmap generated successfully.')


if __name__ == '__main__':
    features = [
        {'name': 'Feature A', 'description': 'Description for Feature A', 'tech': ['Scala', 'Terraform']},
        {'name': 'Feature B', 'description': 'Description for Feature B', 'tech': ['Clojure']},
        {'name': 'Feature C', 'description': 'Description for Feature C', 'tech': ['Terraform']}
    ]
    
    tech_stack = ['Scala', 'Terraform', 'Clojure']
    timeline = {
        'Q1': ['Feature A', 'Feature B'],
        'Q2': ['Feature C']
    }
    
    generate_roadmap(features, tech_stack, timeline)