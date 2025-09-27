import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { toast } from '@/hooks/use-toast';
import { Eye, EyeOff, UserPlus, CheckCircle, XCircle, AlertCircle } from 'lucide-react';

// API конфигурация
const API_BASE_URL = process.env.NODE_ENV === 'production' ? '/api' : 'http://localhost:3000/api';
const REGISTRATION_ENDPOINT = `${API_BASE_URL}/register`;

// Схема валидации
const registrationSchema = z.object({
  login: z
    .string()
    .min(3, { message: 'Логин должен содержать минимум 3 символа' })
    .max(20, { message: 'Логин должен содержать максимум 20 символов' })
    .regex(/^[a-zA-Z0-9_]+$/, { message: 'Логин может содержать только буквы, цифры и подчеркивания' }),
  password: z
    .string()
    .min(8, { message: 'Пароль должен содержать минимум 8 символов' })
    .regex(/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]/, {
      message: 'Пароль должен содержать заглавную букву, строчную букву, цифру и специальный символ'
    }),
  confirmPassword: z.string()
}).refine((data) => data.password === data.confirmPassword, {
  message: 'Пароли не совпадают',
  path: ['confirmPassword']
});

type RegistrationFormData = z.infer<typeof registrationSchema>;

const RegistrationForm = () => {
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
    watch
  } = useForm<RegistrationFormData>({
    resolver: zodResolver(registrationSchema),
    mode: 'onChange'
  });

  const watchedLogin = watch('login');
  const watchedPassword = watch('password');

  // Проверка силы пароля
  const getPasswordStrength = (password: string) => {
    if (!password) return { strength: 0, label: '', color: '' };
    
    let strength = 0;
    if (password.length >= 8) strength++;
    if (/[a-z]/.test(password)) strength++;
    if (/[A-Z]/.test(password)) strength++;
    if (/\d/.test(password)) strength++;
    if (/[@$!%*?&]/.test(password)) strength++;

    const labels = ['Очень слабый', 'Слабый', 'Средний', 'Хороший', 'Отличный'];
    const colors = ['text-destructive', 'text-warning', 'text-yellow-500', 'text-blue-500', 'text-success'];

    return {
      strength,
      label: labels[strength - 1] || '',
      color: colors[strength - 1] || ''
    };
  };

  const passwordStrength = getPasswordStrength(watchedPassword);


  const onSubmit = async (data: RegistrationFormData) => {
    setIsLoading(true);

    try {
      // Отправка запроса на backend
      const response = await fetch(REGISTRATION_ENDPOINT, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          login: data.login,
          password: data.password,
          confirmPassword: data.confirmPassword
        })
      });

      const responseData = await response.json();

      if (response.ok && responseData.success) {
        // Успешная регистрация
        toast({
          title: 'Регистрация успешна!',
          description: responseData.message || `Добро пожаловать, ${data.login}!`,
          className: 'border-success text-success-foreground bg-success/10'
        });
        reset();
      } else {
        // Ошибка регистрации
        toast({
          variant: 'destructive',
          title: 'Ошибка регистрации',
          description: responseData.error || responseData.message || 'Не удалось зарегистрировать пользователя'
        });
      }
    } catch (error) {
      console.error('Registration error:', error);
      toast({
        variant: 'destructive',
        title: 'Ошибка соединения',
        description: 'Не удалось подключиться к серверу. Проверьте соединение.'
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4 animate-fade-in">
      <Card className="w-full max-w-md glass-card shadow-2xl animate-slide-up">
        <CardHeader className="text-center space-y-2">
          <CardTitle className="text-2xl font-bold gradient-text flex items-center justify-center gap-2">
            <UserPlus className="w-6 h-6" />
            Регистрация
          </CardTitle>
          <CardDescription className="text-muted-foreground">
            Создайте новый аккаунт для входа в систему
          </CardDescription>
        </CardHeader>
        
        <CardContent>
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
            {/* Поле логина */}
            <div className="space-y-2">
              <Label htmlFor="login" className="text-sm font-medium">
                Логин
              </Label>
              <div className="relative">
                <Input
                  id="login"
                  type="text"
                  placeholder="Введите логин"
                  {...register('login')}
                  className={`${errors.login ? 'border-destructive focus-visible:ring-destructive' : ''}`}
                />
                {watchedLogin && !errors.login && (
                  <div className="absolute right-3 top-1/2 transform -translate-y-1/2">
                    <CheckCircle className="w-5 h-5 text-success" />
                  </div>
                )}
              </div>
              {errors.login && (
                <p className="text-sm text-destructive flex items-center gap-1">
                  <AlertCircle className="w-4 h-4" />
                  {errors.login.message}
                </p>
              )}
            </div>

            {/* Поле пароля */}
            <div className="space-y-2">
              <Label htmlFor="password" className="text-sm font-medium">
                Пароль
              </Label>
              <div className="relative">
                <Input
                  id="password"
                  type={showPassword ? 'text' : 'password'}
                  placeholder="Введите пароль"
                  {...register('password')}
                  className={`pr-10 ${errors.password ? 'border-destructive focus-visible:ring-destructive' : ''}`}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 transform -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors"
                >
                  {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                </button>
              </div>
              
              {/* Индикатор силы пароля */}
              {watchedPassword && (
                <div className="space-y-2">
                  <div className="flex justify-between items-center">
                    <span className="text-xs text-muted-foreground">Сила пароля:</span>
                    <span className={`text-xs font-medium ${passwordStrength.color}`}>
                      {passwordStrength.label}
                    </span>
                  </div>
                  <div className="w-full bg-muted rounded-full h-2">
                    <div
                      className={`h-full rounded-full transition-all duration-300 ${
                        passwordStrength.strength === 1 ? 'bg-destructive w-1/5' :
                        passwordStrength.strength === 2 ? 'bg-warning w-2/5' :
                        passwordStrength.strength === 3 ? 'bg-yellow-500 w-3/5' :
                        passwordStrength.strength === 4 ? 'bg-blue-500 w-4/5' :
                        passwordStrength.strength === 5 ? 'bg-success w-full' : 'w-0'
                      }`}
                    />
                  </div>
                </div>
              )}
              
              {errors.password && (
                <p className="text-sm text-destructive flex items-center gap-1">
                  <AlertCircle className="w-4 h-4" />
                  {errors.password.message}
                </p>
              )}
            </div>

            {/* Подтверждение пароля */}
            <div className="space-y-2">
              <Label htmlFor="confirmPassword" className="text-sm font-medium">
                Подтвердите пароль
              </Label>
              <div className="relative">
                <Input
                  id="confirmPassword"
                  type={showConfirmPassword ? 'text' : 'password'}
                  placeholder="Повторите пароль"
                  {...register('confirmPassword')}
                  className={`pr-10 ${errors.confirmPassword ? 'border-destructive focus-visible:ring-destructive' : ''}`}
                />
                <button
                  type="button"
                  onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                  className="absolute right-3 top-1/2 transform -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors"
                >
                  {showConfirmPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                </button>
              </div>
              {errors.confirmPassword && (
                <p className="text-sm text-destructive flex items-center gap-1">
                  <AlertCircle className="w-4 h-4" />
                  {errors.confirmPassword.message}
                </p>
              )}
            </div>

            {/* Кнопка регистрации */}
            <Button
              type="submit"
              variant="gradient"
              className="w-full h-12 text-base font-semibold"
              disabled={isLoading}
            >
              {isLoading ? (
                <div className="flex items-center gap-2">
                  <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  Регистрация...
                </div>
              ) : (
                <div className="flex items-center gap-2">
                  <UserPlus className="w-5 h-5" />
                  Зарегистрироваться
                </div>
              )}
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
};

export default RegistrationForm;