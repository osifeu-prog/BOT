#!/bin/bash
# 🚀 NFTY ULTRA PRO - Deployment Script
# סקריפט פריסה אוטומטי עם בדיקות ומעקב

set -e  # יצא על שגיאה

# הגדרות צבעים
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# פונקציות עזר
print_step() {
    echo -e "${BLUE}▶${NC} $1"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# בדיקת דרישות מוקדמות
check_requirements() {
    print_step "בדיקת דרישות מערכת..."
    
    # בדוק אם Docker מותקן
    if ! command -v docker &> /dev/null; then
        print_error "Docker אינו מותקן!"
        exit 1
    fi
    
    # בדוק אם Docker Compose מותקן
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose אינו מותקן!"
        exit 1
    fi
    
    # בדוק אם Git מותקן
    if ! command -v git &> /dev/null; then
        print_error "Git אינו מותקן!"
        exit 1
    fi
    
    # בדוק אם Python מותקן
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 אינו מותקן!"
        exit 1
    fi
    
    print_success "כל הדרישות מתקיימות"
}

# בדיקת קבצי תצורה
check_config_files() {
    print_step "בדיקת קבצי תצורה..."
    
    required_files=(
        ".env"
        "docker-compose.yml"
        "requirements.txt"
        "Main.py"
        "config.py"
    )
    
    missing_files=()
    
    for file in "${required_files[@]}"; do
        if [ ! -f "$file" ]; then
            missing_files+=("$file")
        fi
    done
    
    if [ ${#missing_files[@]} -gt 0 ]; then
        print_error "קבצים חסרים:"
        for file in "${missing_files[@]}"; do
            echo "  - $file"
        done
        exit 1
    fi
    
    print_success "כל קבצי התצורה קיימים"
}

# הרצת בדיקות
run_tests() {
    print_step "הרצת בדיקות..."
    
    # בדיקות Python
    if python3 -m pytest tests/ -v --tb=short; then
        print_success "כל הבדיקות עברו בהצלחה"
    else
        print_error "חלק מהבדיקות נכשלו"
        exit 1
    fi
    
    # בדיקות Docker
    if docker-compose config --quiet; then
        print_success "תצורת Docker תקינה"
    else
        print_error "תצורת Docker שגויה"
        exit 1
    fi
}

# בניית Docker images
build_images() {
    print_step "בניית Docker images..."
    
    # נקה images ישנים
    docker system prune -f
    
    # בנה images חדשים
    if docker-compose build --no-cache --pull; then
        print_success "Images נבנו בהצלחה"
    else
        print_error "בניית Images נכשלה"
        exit 1
    fi
}

# עצירת containers קיימים
stop_containers() {
    print_step "עצירת containers קיימים..."
    
    if docker-compose down --remove-orphans; then
        print_success "Containers נעצרו בהצלחה"
    else
        print_warning "לא ניתן לעצור את כל ה-containers"
    fi
}

# הפעלת המערכת
start_system() {
    print_step "הפעלת המערכת..."
    
    # הרץ את המערכת בפרונטגראונד
    if docker-compose up -d --force-recreate; then
        print_success "המערכת הופעלה בהצלחה"
    else
        print_error "הפעלת המערכת נכשלה"
        exit 1
    fi
    
    # המתן לאתחול
    sleep 10
    
    # בדוק סטטוס
    check_system_status
}

# בדיקת סטטוס המערכת
check_system_status() {
    print_step "בדיקת סטטוס המערכת..."
    
    services=("bot" "redis" "prometheus" "grafana")
    
    all_healthy=true
    
    for service in "${services[@]}"; do
        if docker-compose ps "$service" | grep -q "Up"; then
            print_success "$service: פועל"
        else
            print_error "$service: לא פועל"
            all_healthy=false
        fi
    done
    
    if [ "$all_healthy" = true ]; then
        print_success "כל השירותים פועלים"
        
        # בדוק health endpoints
        check_health_endpoints
    else
        print_error "חלק מהשירותים אינם פועלים"
        show_logs
        exit 1
    fi
}

# בדיקת health endpoints
check_health_endpoints() {
    print_step "בדיקת health endpoints..."
    
    endpoints=(
        "http://localhost:8080/health"
        "http://localhost:9091/-/healthy"
        "http://localhost:3000/api/health"
    )
    
    for endpoint in "${endpoints[@]}"; do
        if curl -s -f "$endpoint" > /dev/null; then
            print_success "$endpoint: זמין"
        else
            print_error "$endpoint: לא זמין"
        fi
    done
}

# הצגת לוגים
show_logs() {
    print_step "הצגת לוגים אחרונים..."
    
    docker-compose logs --tail=50 bot
    docker-compose logs --tail=20 redis
}

# גיבוי נתונים
backup_data() {
    print_step "גיבוי נתונים..."
    
    timestamp=$(date +%Y%m%d_%H%M%S)
    backup_dir="backups/$timestamp"
    
    mkdir -p "$backup_dir"
    
    # גבה Redis
    if docker-compose exec redis redis-cli SAVE; then
        docker cp "$(docker-compose ps -q redis)":/data/dump.rdb "$backup_dir/redis.rdb"
        print_success "Redis גובה בהצלחה"
    else
        print_error "גיבוי Redis נכשל"
    fi
    
    # גבה קבצי יישום
    tar -czf "$backup_dir/app.tar.gz" \
        --exclude='__pycache__' \
        --exclude='*.pyc' \
        --exclude='*.log' \
        --exclude='backups' \
        .
    
    print_success "גיבוי הושלם: $backup_dir"
}

# ניקוי resources ישנים
cleanup() {
    print_step "ניקוי resources ישנים..."
    
    # מחק Docker images ישנים
    docker image prune -f
    
    # מחק containers לא פעילים
    docker container prune -f
    
    # מחק volumes לא בשימוש
    docker volume prune -f
    
    # מחק קבצי cache
    find . -type d -name "__pycache__" -exec rm -rf {} +
    find . -type f -name "*.pyc" -delete
    
    print_success "ניקוי הושלם"
}

# הצגת מידע פריסה
show_deployment_info() {
    print_step "מידע פריסה:"
    
    echo ""
    echo "🎰 NFTY ULTRA PRO הופעל בהצלחה!"
    echo ""
    echo "📊 ממשקי ניהול:"
    echo "  • הבוט: http://localhost:8080"
    echo "  • Redis Commander: http://localhost:8081"
    echo "  • Grafana (דשבורדים): http://localhost:3000"
    echo "  • Prometheus (מדידות): http://localhost:9091"
    echo "  • Adminer (DB): http://localhost:8082"
    echo ""
    echo "📈 סטטיסטיקות:"
    docker-compose ps
    echo ""
    echo "📋 לוגים:"
    echo "  צפה בלוגים: docker-compose logs -f bot"
    echo "  עצירה: docker-compose down"
    echo ""
}

# פונקציה ראשית
main() {
    echo ""
    echo "🚀 NFTY ULTRA PRO - Automated Deployment"
    echo "========================================"
    echo ""
    
    # פרמטרים
    case "${1:-}" in
        "test")
            check_requirements
            check_config_files
            run_tests
            ;;
        "build")
            check_requirements
            check_config_files
            build_images
            ;;
        "deploy")
            check_requirements
            check_config_files
            run_tests
            backup_data
            stop_containers
            build_images
            start_system
            cleanup
            show_deployment_info
            ;;
        "backup")
            backup_data
            ;;
        "clean")
            cleanup
            ;;
        "status")
            check_system_status
            ;;
        "logs")
            show_logs
            ;;
        "stop")
            stop_containers
            ;;
        "start")
            start_system
            ;;
        *)
            echo "שימוש: $0 {test|build|deploy|backup|clean|status|logs|stop|start}"
            echo ""
            echo "פקודות:"
            echo "  test    - הרץ בדיקות"
            echo "  build   - בנה Docker images"
            echo "  deploy  - פריסה מלאה"
            echo "  backup  - גיבוי נתונים"
            echo "  clean   - נקה resources"
            echo "  status  - הצג סטטוס"
            echo "  logs    - הצג לוגים"
            echo "  stop    - עצור מערכת"
            echo "  start   - הפעל מערכת"
            exit 1
            ;;
    esac
}

# הרץ את הפונקציה הראשית
main "$@"
