# Quick test script to verify API functionality

$baseUrl = "http://localhost:8000"

Write-Host "🧪 Testing Soft Skill Practice Service API" -ForegroundColor Green

# Test health check
Write-Host "Testing health check..." -ForegroundColor Blue
try {
    $health = Invoke-RestMethod -Uri "$baseUrl/health/" -Method GET
    Write-Host "✅ Health check passed: $($health.status)" -ForegroundColor Green
} catch {
    Write-Host "❌ Health check failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Test get soft skills
Write-Host "Testing get soft skills..." -ForegroundColor Blue
try {
    $skills = Invoke-RestMethod -Uri "$baseUrl/soft-skills/" -Method GET
    Write-Host "✅ Found $($skills.Count) soft skills" -ForegroundColor Green
    $skills | ForEach-Object { Write-Host "  • $($_.name)" -ForegroundColor White }
} catch {
    Write-Host "❌ Get soft skills failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test get scenarios for first skill
if ($skills -and $skills.Count -gt 0) {
    $firstSkillId = $skills[0].id
    Write-Host "Testing get scenarios for skill ID $firstSkillId..." -ForegroundColor Blue
    try {
        $scenarios = Invoke-RestMethod -Uri "$baseUrl/soft-skills/$firstSkillId/scenarios" -Method GET
        Write-Host "✅ Found $($scenarios.Count) scenarios" -ForegroundColor Green
        $scenarios | ForEach-Object { Write-Host "  • $($_.title)" -ForegroundColor White }
    } catch {
        Write-Host "❌ Get scenarios failed: $($_.Exception.Message)" -ForegroundColor Red
    }
    
    # Test start practice session
    if ($scenarios -and $scenarios.Count -gt 0) {
        $firstScenarioId = $scenarios[0].id
        Write-Host "Testing start practice session..." -ForegroundColor Blue
        try {
            $startRequest = @{
                user_id = "test_user_api_test"
                soft_skill_id = $firstSkillId
                scenario_id = $firstScenarioId
            } | ConvertTo-Json
            
            $session = Invoke-RestMethod -Uri "$baseUrl/practice/start" -Method POST -Body $startRequest -ContentType "application/json"
            Write-Host "✅ Practice session started: $($session.session_id)" -ForegroundColor Green
            
            # Test submit practice
            Write-Host "Testing submit practice..." -ForegroundColor Blue
            $submitRequest = @{
                session_id = $session.session_id
                user_input = "This is a test response for the API testing. I would handle this situation with professionalism and empathy."
                duration_seconds = 180
            } | ConvertTo-Json
            
            $result = Invoke-RestMethod -Uri "$baseUrl/practice/submit" -Method POST -Body $submitRequest -ContentType "application/json"
            Write-Host "✅ Practice submitted successfully" -ForegroundColor Green
            Write-Host "  • Overall Score: $($result.scores.overall_score)" -ForegroundColor White
            Write-Host "  • Points Earned: $($result.points_earned)" -ForegroundColor White
            
            # Test get user progress
            Write-Host "Testing get user progress..." -ForegroundColor Blue
            $progress = Invoke-RestMethod -Uri "$baseUrl/progress/test_user_api_test" -Method GET
            Write-Host "✅ User progress retrieved" -ForegroundColor Green
            Write-Host "  • Total Points: $($progress.total_points)" -ForegroundColor White
            Write-Host "  • Completed Practices: $($progress.total_completed_practices)" -ForegroundColor White
            
        } catch {
            Write-Host "❌ Practice flow failed: $($_.Exception.Message)" -ForegroundColor Red
        }
    }
}

Write-Host ""
Write-Host "🎉 API testing completed!" -ForegroundColor Green
