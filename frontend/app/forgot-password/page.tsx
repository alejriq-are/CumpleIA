import { ForgotPasswordForm } from "@/components/auth/ForgotPasswordForm";

export default function ForgotPasswordPage() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-50 px-4">
      <div className="w-full max-w-md space-y-8 rounded-xl bg-white p-8 shadow-md">
        <div>
          <h1 className="text-3xl font-bold text-blue-800">CumpleIA</h1>
          <p className="mt-2 text-sm text-gray-500">Recupera el acceso a tu cuenta</p>
        </div>
        <ForgotPasswordForm />
      </div>
    </div>
  );
}
