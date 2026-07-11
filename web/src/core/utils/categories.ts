const CATEGORY_LABELS: Record<string, string> = {
  FOOD: "Alimentos",
  DINING_OUT: "Comida fuera",
  TRANSPORTATION: "Transporte",
  ENTERTAINMENT: "Entretenimiento",
  SPORTS: "Deportes",
  HEALTH: "Salud",
  SHOPPING: "Compras",
  EDUCATION: "Educación",
  HOME: "Hogar",
  SALARY: "Salario",
  FREELANCE: "Independiente",
  INVESTMENTS: "Inversiones",
  OTHER: "Otro",
};

export function categoryLabel(category: string): string {
  return CATEGORY_LABELS[category] || category;
}
